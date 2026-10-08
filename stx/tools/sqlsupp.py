'''
Module providing the SQL interface for other parts of the package.
'''

import io
import sqlite3

class SqlSupportError(ValueError):
  pass

class SqlSupport:
  '''Class providing a wrapper around the particular SQL engine in use'''
  def __init__(self, dbname, debug=False, sql_debug=False):
    self.conn = sqlite3.connect(dbname)
    self._debug, self._sql_debug = debug, sql_debug

  def __del__(self):
    self.conn.close()

  def create_table(self, tabname, primkey, **columns):
    'Create a table TABNAME with COLUMNS and a primay index PRIMKEY'
    if not columns:
      raise SqlSupportError('Cannot create table without columns')
    sql_stmt = io.StringIO()
    sql_stmt.write(f'CREATE TABLE IF NOT EXISTS {tabname} (')
    if primkey is None:
      sgl_prim = None
    elif isinstance(primkey, (tuple, list)):
      for pk in primkey:
        if pk not in columns:
          raise SqlSupportError(f'Primary key contains an invalid column:, {pk}')
      primkey = ', '.join(primkey)
      sgl_prim = 0
    elif not isinstance(primkey, str):
      raise SqlSupportError('Invalid primary key given')
    elif primkey.find(',') > 0:
      raise SqlSupportError('Primary key must be a single column or a sequence of columns')
    elif primkey not in columns:
      raise SqlSupportError(f'Primary key is not a valid column: {primkey}')
    else:
      sgl_prim = 1

    do_comma = False
    for nm, ty in columns.items():
      if do_comma:
        sql_stmt.write(', ')
      else:
        do_comma = True
      if issubclass(ty, (int, bool)):
        sql_stmt.write(f'{nm} INTEGER')
      elif issubclass(ty, str):
        sql_stmt.write(f'{nm} TEXT')
      elif issubclass(ty, float):
        sql_stmt.write(f'{nm} REAL')
      else:
        raise SqlSupportError(f'Invalid column type: {nm} -> {ty}')
      if sgl_prim is None or (sgl_prim == 1 and nm == primkey):
        sgl_prim = 2
        sql_stmt.write(' PRIMARY KEY')
    if sgl_prim == 0:
      sql_stmt.write(f', PRIMARY KEY ({primkey})')
    sql_stmt.write(')')
    if self._sql_debug:
      print('CREATE_TABLE:', sql_stmt.getvalue())
    self.conn.execute(sql_stmt.getvalue())
    sql_stmt.close()

  def create_index(self, tabname, idxname, idxuniq, *idxparts):
    'Create an index IDXNAME on table TABNAME with parts IDXPARTS'
    if not idxparts:
      raise SqlSupportError('Cannot create index with no parts')
    sql_stmt = io.StringIO()
    if idxuniq:
      sql_stmt.write('CREATE UNIQUE INDEX IF NOT EXISTS ')
    else:
      sql_stmt.write('CREATE INDEX IF NOT EXISTS ')
    sql_stmt.write(idxname)
    sql_stmt.write(' ON ')
    sql_stmt.write(tabname)
    sql_stmt.write(' (')
    do_comma = False
    for part in idxparts:
      if do_comma:
        sql_stmt.write(', ')
      else:
        do_comma = True
      sql_stmt.write(part)
    sql_stmt.write(')')
    if self._sql_debug:
      print('CREATE_INDEX:', sql_stmt.getvalue())
    # self.conn.execute(sql_stmt.getvalue())            # TODO: Enable creation of indexes
    sql_stmt.close()

  def _merge_arg_kwds(self, *args, **kwds):
    'Merge ARGS into KWDS'
    for arg in args:
      if isinstance(arg, dict):
        kwds.update(arg)
      elif isinstance(arg, tuple):
        if len(arg) == 2:
          kwds[arg[0]] = arg[1]
        
  # NOTE: Need to describe table for both INSERT and UPDATE to enable control of valid column names and values.
  def _describe_table_coltype(self, tabname):
    'Return a sequence providing the definition of TABNAME including name and type'
    curs = self.conn.execute(f"SELECT name, type FROM pragma_table_info('{tabname}')")
    defn = list()
    for dn, dt in curs:
      match dt:
        case 'INTEGER':
          defn.append((dn, int))
        case 'TEXT':
          defn.append((dn, str))
        case 'REAL':
          defn.append((dn, float))
        case _:
          raise SqlSupportError(f'DEFN: Unhandled type of column: {dn}: {dt}')
    return defn
    
  def _describe_table_colname(self, tabname):
    'Return the columns making up the given TABNAME'
    curs = self.conn.execute(f"SELECT name FROM pragma_table_info('{tabname}')")
    return [r[0] for r in curs]
  
  def _gen_col_list(self, sql_stmt, colfmt, coliter, sep=', '):
    'Generate a column list using COLFMT and separated by SEP using COLITER'
    do_sep = False
    for name in coliter:
      if isinstance(name, tuple):
        name = name[0]
      if do_sep:
        sql_stmt.write(sep)
      else:
        do_sep = True
      sql_stmt.write(colfmt.format(name=name))
      
  def _gen_where(self, sql_stmt, values, where=None):
    '''Generate the where clause which has the format:
    {column: value} or {column: (operator, value)}
    TODO: Need to add handling of columns and where operators correctly.
    '''
    if where is None:
      return values
    elif not isinstance(where, dict):
      raise SqlSupportError('Pass a dictionary of where clauses or None')
    sql_stmt.write(' WHERE ')
    do_and = False
    for col, chk in where.items():
      if do_and:
        sql_stmt.write(' AND ')
      else:
        do_and = True
      if isinstance(chk, tuple):
        if len(chk) != 2 or not isinstance(col[0], str):
          raise SqlSupportError('Must provide a tuple of (OPERATOR, VALUE)')
        if chk[0] in ('=', '!=', '>', '>=', '<', '<='):
          sql_stmt.write(f'{col}{chk[0]}:{col}')
          values[col] = chk[1]
        else:
          raise SqlSupportError(f'Unhandled operator: {chk[0]}')
      else:
        sql_stmt.write(f'{col}=:{col}')
        values[col] = chk
    return values
      
  def insert(self, tabname, values):
    'Insert the given values into the specified table'
    if not isinstance(values, dict):
      SqlSupportError('Must pass a dictionary of values to be inserted')
    sql_stmt = io.StringIO()
    sql_stmt.write(f'INSERT INTO {tabname} VALUES (')
    self._gen_col_list(sql_stmt, ':{name}', self.conn.execute(f"SELECT name FROM pragma_table_info('{tabname}')"))
    sql_stmt.write(')')
    if self._sql_debug:
      print('INSERT:', sql_stmt.getvalue(), values)
    self.conn.execute(sql_stmt.getvalue(), values)

  def update(self, tabname, columns, where):
    'Update the specified COLUMNS with optional WHERE clause and given values'
    # TODO: Need to handle columns and where clauses correctly.
    if not isinstance(columns, dict):
      raise SqlSupportError('Pass a dictionary of columns with values to be updated to')
    dbdata = {}
    dbdata.update(columns)
    sql_stmt = io.StringIO()
    sql_stmt.write(f'UPDATE {tabname} SET ')
    self._gen_col_list(sql_stmt, '{name}=:{name}', columns.keys())
    self._gen_where(sql_stmt, dbdata, where)
    if self._sql_debug:
      print('SQL_UPDATE:', sql_stmt.getvalue(), dbdata)
    self.conn.execute(sql_stmt.getvalue(), dbdata)

  def select(self, tabname, columns=None, *, where=None, limit=None):
    'Generate a select statement on TABNAME returning COLUMNS with optional WHERE and LIMIT'
    sql_stmt = io.StringIO()
    sql_stmt.write('SELECT ')
    if isinstance(columns, (tuple, list)):
      sql_stmt.write(', '.join(columns))
    elif isinstance(columns, str):
      if ',' in columns:
        raise SqlSupportError('Multiple columns must be passed as a sequence')
      sql_stmt.write(columns)
    else:
      sql_stmt.write('*')
    sql_stmt.write(f' FROM {tabname}')
    values = dict()
    self._gen_where(sql_stmt, values, where)
    if isinstance(limit, int):
      sql_stmt.write(f' LIMIT {limit}')
      single = limit == 1
    else:
      single = False
    if self._sql_debug:
      print('SELECT:', sql_stmt.getvalue(), values)
    if where:
      rows = self.conn.execute(sql_stmt.getvalue(), values)
    else:
      rows = self.conn.execute(sql_stmt.getvalue())
    if single:
      if row := rows.fetchone():
        return row[0] if isinstance(columns, str) else row
      return None
    else:
      return rows    
    
  def select_all(self, tabname, columns=None):
    return self.select(tabname, columns)

  def select_limit(self, tabname, columns=None, limit=1):
    return self.select(tabname, columns, limit=limit)

  def select_where(self, tabname, columns=None, where=None):
    return self.select(tabname, columns, where=where)
  
  def commit(self):
    'Commit any outstanding changes to the database'
    self.conn.commit()
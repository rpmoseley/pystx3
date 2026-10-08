sqlite3 uk_format.db << EOF
delete from control where entity='$1';
delete from format where entity='$1';
delete from field where entity='$1';
delete from fixtext where entity='$1';
delete from fixbox where entity='$1';
EOF

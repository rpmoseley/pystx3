Graph Call of Software
======================
This file provides an overview of the classes provided by the various submodules within the package, this is required to avoid problems with duplicate classes providing the same
or similar functionality and causing problems getting the software to work.

- driver/appl/command/base
- driver/appl/command/debug
- driver/appl/command/mapping
- driver/appl/command/nonui
- driver/appl/comms/legacy
- driver/appl/comms/pipe
- driver/appl/comms/protocol
- driver/appl/comms/socketpair
- driver/appl/stack
- driver/appl/ui/base
- driver/appl/ui/non/debug

driver/appl/command/base
''''''''''''''''''''''''
1. Includes:
   a. .mapping.CommandMap
2. Class CommandBase
   a. process_command(cmd)
3. Class GroupDefaultBase(dict)
   a. set(group, value, typ=None)
   b. get(group, typ=None)

driver/appl/command/debug
'''''''''''''''''''''''''
1. Includes:
   a. .nonui
   b. appl.stack.WindowStack
   c. appl.stack.PopemenuStack
   d. screen.format.FieldAction
2. Class GroupDefault(nonui.GroupDefault)
   a. Set(group, value, typ=None)
   b. Get(group, typ=None)
3. Class Command(nonui.Command)
   aa. DumpString(val)
   ab. cmd_Background(cmd)
   ac. cmd_PrModify(cmd)
   ad. cmd_SetCurrency(cmd)
   ae. cmd_ShowHelp(cmd)
   af. cmd_ScrUpd(cmd)
   ag. cmd_MentorWord(cmd)
   ah. cmd_GetGName(cmd)
   ai. cmd_PrDup(cmd)
   aj. cmd_FindVT(cmd)
   ak. cmd_SystemRequest(cmd)
   al. cmd_GPGet(cmd)
   am. cmd_GPUpdate(cmd)
   an. cmd_FastExit(cmd)
   ao. cmd_PopOpen(cmd)
   ap. cmd_PopClose(cmd)
   aq. cmd_PopOnOff(cmd)
   ar. cmd_PopAt(cmd)
   as. cmd_PopText(cmd)
   at. cmd_PopCreate(cmd)
   au. cmd_PopAmend(cmd)
   av. cmd_PopDelete(cmd)
   aw. cmd_PopData(cmd)
   ax. cmd_CanRun(cmd)
   ay. cmd_AppReadChar(cmd)
   az. cmd_OpenWindow(cmd)
   ba. cmd_RunProgram(cmd)
   bb. cmd_ClearFormat(cmd)
   bc. cmd_DetachMe(cmd)
   bd. cmd_ChangeLength(cmd)
   be. cmd_ChangeMessage(cmd)
   bf. cmd_InterruptOn(cmd)
   bg. cmd_InterruptOff(cmd)
   bh. cmd_MessageOn(cmd)
   bi. cmd_MessageOff(cmd)
   bj. cmd_KillMe(cmd)
   bk. cmd_LoadFormat(cmd)
   bl. cmd_MessageScreen(cmd)
   bm. cmd_StartPrint(cmd)
   bn. cmd_NewPrint(cmd)
   bo. cmd_FormData(cmd)
   bp. cmd_ReadFormat(cmd)
   bq. cmd_SuspendMe(cmd)
   br. cmd_TitleScreen(cmd)
   bs. cmd_EndPrint(cmd)
   bt. cmd_DebugMenu(cmd)
   bu. cmd_WriteFromat(cmd)
   bv. cmd_ChangePosition(cmd)
   bw. _vldtype
   bx. cmd_ChangeType(cmd)
   by. cmd_TraceLevel(cmd)
   bz. cmd_PrNewJob(cmd)
   ca. cmd_WriteMessage(cmd)
   cb. cmd_CloseMessage(cmd)
   cc. cmd_Blank(cmd)
   cd. cmd_ClearScreen(cmd)
   ce. cmd_WipeFormat(cmd)
   cf. cmd_DeDump(cmd)
   cg. cmd_LoseChar(cmd)
   ch. cmd_NameWindow(cmd)
   ci. cmd_TypeAhead(cmd)
   cj. cmd_SizeWind(cmd)
   ck. cmd_FormNLoad(cmd)
   cl. cmd_IsWindDisplay(cmd)
   cm. cmd_LogComment(cmd)
   cn. cmd_WindDefine(cmd)
   co. cmd_NumberDecimals(cmd)
   cp. cmd_WindData(cmd)
   cq. cmd_PrintScreen(cmd)
   cr. cmd_Repeats(cmd)
   cs. cmd_FldCurr(cmd)
   ct. cmd_SetDecimals(cmd)
   cu. cmd_ToolInfo(cmd)
   cv. cmd_LastChar(cmd)
   cw. cmd_ScrollDir(cmd)
   cx. cmd_WidthScreen(cmd)
   cy. cmd_KeyWait(cmd)
   cz. cmd_FormFLoad(cmd)
   da. cmd_GetVirtual(cmd)
   db. cmd_IsSuspended(cmd)
   dc. cmd_AppHotKey(cmd)
   dd. cmd_PTitleScreen(cmd)

driver/appl/command/mapping
'''''''''''''''''''''''''''
1. Class GroupDefaultBase(dict)
   a. Set(group, value, typ=None)
   b. Get(group, typ=None)
2. Class CommandMap
   a. _map

driver/appl/command/nonui
'''''''''''''''''''''''''
1. Includes:
   a. .mapping.CommandMap
   b. .base.CommandBase
   c. .base.GroupDefaultBase
2. Class Command(CommandBase)
3. Class GroupDefault(GroupDefaultBase)

driver/appl/comms/legacy
''''''''''''''''''''''''
1. Includes:
   a. os
   b. struct
   c. __init__.CommMixin
2. Class Comm(CommMixin)
   aa. receive(fmt)
   ab. recv_command()
   ac. recv_char()
   ad. recv_byte()
   ae. recv_bool()
   af. recv_short()
   ag. recv_long()
   ah. recv_record()
   ai. recv_string()
   aj. recv_compress()
   ak. send(fmt, \*vals)
   al. send_char(val)
   am. send_bool(val)
   an. send_byte(val)
   ao. send_short(val)
   ap. send_string(val)
   aq. send_compress(val)

driver/appl/comms/pipe
''''''''''''''''''''''
1. Includes
   a. fcntl
   b. os
   c. resource
2. Class CommMixin
   a. open(appl, resfd=None, env=None, \*args)
   b. close()
   c. read(numbyte)
   d. write(byteval)

driver/appl/comms/protocol
''''''''''''''''''''''''''
1. Includes
   a. os
   b. struct
   c. __init__.CommMixin
2. Class Comm(CommMixin)
   a. recv_command()
   b. recv_char()
   c. recv_byte()
   d. recv_bool()
   e. recv_short()
   f. recv_long()
   g. recv_record()
   h. recv_string()
   i. recv_compress()
   j. send_char(val)
   k. send_byte(val)
   l. send_short(val)
   m. send_string(val)
   n. send_compress(val)
3. Class CommVersion
4. Class CommProtocol(AppComm)
   a. RecvItem(valsiz)
   b. SendItem(val)

driver/appl/comms/socketpair
''''''''''''''''''''''''''''
1. Includes
   a. os
   b. resource
   c. socket
2. Class CommMixin
   a. open(appl, resfd=None, env=None, \*args)
   b. close()
   c. read(numbyte)
   d. write(byteval)

driver/appl/stack
'''''''''''''''''
1. Includes
   a. screen.control.WindowControl
   b. screen.control.PopControl
   c. screen.control.FormatControl
   d. screen.cache.ScreenCache
2. Class WindowStack
   a. Open(name, usrmde=False, coid=None, user=None, lang=None)
   b. Close(name)
   c. AddFormat(form, chksum=0, rep=1)
   d. Active()
   e. ActiveFormat()
3. Class PopmenuStack(WindowStack)
   a. Open(name, initopt=None, usrmde=False, coid=None, user=None, lang=None, onoff=None)
   b. Close(name)

driver/appl/ui/base
'''''''''''''''''''
1. Includes:
   a. appl.stack.WindowControl
   b. appl.stack.PopControl
   c. appl.stack.FormatControl
2. Class UserProcessorBase
   a. Handle(action)

driver/appl/ui/non/debug
''''''''''''''''''''''''
1. Class Processor
   a. ui_PopMenu(ent)
   b. ui_Format(ent)

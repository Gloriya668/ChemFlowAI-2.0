"""Rebuild the included GPL DWSIM MCP sources against the pinned official runtime."""
import argparse
import json
import shutil
import subprocess
from pathlib import Path
from xml.sax.saxutils import escape

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--runtime',required=True,help='DWSIM 10.2.11 portable directory')
parser.add_argument('--dotnet',default='dotnet',help='.NET 10 SDK dotnet executable')
args=parser.parse_args()
runtime=Path(args.runtime).resolve()
source=root/'tools/dwsim-mcp-src'
project=source/'ChemFlow.MCP.csproj'
refs=['DWSIM*.dll','Newtonsoft.Json.dll','SkiaSharp.dll','CapeOpen.dll','ICSharpCode.SharpZipLib.dll']
project.write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework><OutputType>Exe</OutputType><AssemblyName>dwsim-mcp</AssemblyName><ImplicitUsings>disable</ImplicitUsings><Nullable>disable</Nullable></PropertyGroup><ItemGroup>'+''.join('<Reference Include="'+escape(str(runtime/name),{'"':'&quot;'})+'"/>' for name in refs)+'</ItemGroup></Project>',encoding='utf-8')
out=root/'runtime/mcp-build'
subprocess.run([args.dotnet,'build',str(project),'-c','Release','-o',str(out),'--nologo'],check=True)
target=root/'tools/dwsim-mcp-bin';target.mkdir(parents=True,exist_ok=True)
for name in ('dwsim-mcp.exe','dwsim-mcp.dll'):
    shutil.copy2(out/name,target/name)
ui=json.loads((runtime/'DWSIM.UI.Desktop.Avalonia.deps.json').read_text(encoding='utf-8'))
mcp=json.loads((out/'dwsim-mcp.deps.json').read_text(encoding='utf-8'))
lib='dwsim-mcp/1.0.0'
target_entries=ui['targets'][ui['runtimeTarget']['name']]
mcp_entries=next(iter(mcp['targets'].values()))
entry=mcp_entries[lib]
for name,version in list(entry.get('dependencies',{}).items()):
    available=next((key.rsplit('/',1)[1] for key in target_entries if key.rsplit('/',1)[0]==name),None)
    if available:entry['dependencies'][name]=available
    else:
        dependency=name+'/'+version
        target_entries[dependency]=mcp_entries[dependency]
        ui['libraries'][dependency]=mcp['libraries'][dependency]
target_entries[lib]=entry
ui['libraries'][lib]=mcp['libraries'][lib]
(target/'dwsim-mcp.deps.json').write_text(json.dumps(ui,indent=2),encoding='utf-8')
shutil.copy2(runtime/'DWSIM.UI.Desktop.Avalonia.runtimeconfig.json',target/'dwsim-mcp.runtimeconfig.json')
print('Built MCP artifacts:',target)

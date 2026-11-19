"""Run a real water-heater test; never substitutes a fixture for DWSIM."""
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.dwsim_mcp import Session
from backend.store import ROOT


def run():
    trace=[]
    report={'status':'FAILED','trace':trace}
    try:
        with Session(audit=trace) as session:
            fid=session.call('dwsim_flowsheet_create',name='ChemFlow water heater smoke')['flowsheet_id']
            session.call('dwsim_thermo_add_compounds',flowsheet_id=fid,names=['Water'])
            session.call('dwsim_thermo_set_property_package',flowsheet_id=fid,name='Steam Tables (IAPWS-IF97)')
            session.call('dwsim_stream_add_material',flowsheet_id=fid,name='FEED',temperature_K=300.,pressure_Pa=101325.,mass_flow_kg_s=1.,composition={'Water':1.})
            session.call('dwsim_stream_add_material',flowsheet_id=fid,name='PRODUCT')
            session.call('dwsim_stream_add_energy',flowsheet_id=fid,name='HEAT')
            session.call('dwsim_unitop_add',flowsheet_id=fid,type='Heater',name='HEATER')
            session.call('dwsim_unitop_connect',flowsheet_id=fid,unitop='HEATER',feed_stream='FEED',product_stream='PRODUCT',energy_feed='HEAT')
            session.call('dwsim_unitop_set',flowsheet_id=fid,name='HEATER',properties={'CalcMode':'OutletTemperature','OutletTemperature':350.0,'DeltaP':0.0,'Efficiency':100.0})
            report['preflight']=session.call('dwsim_flowsheet_check',flowsheet_id=fid)
            report['solve']=session.call('dwsim_solve_run',flowsheet_id=fid,timeout_s=60)
            if not report['solve']['ok']:raise ValueError('DWSIM solve failed')
            product=session.call('dwsim_stream_get_results',flowsheet_id=fid,name='PRODUCT')
            report['product']=product
            if abs(product['temperature_K']-350)>0.01 or abs(product['mass_flow_kg_s']-1)>1e-6:
                raise ValueError('Temperature / mass balance smoke assertion failed')
            report['heater']=session.call('dwsim_unitop_get_results',flowsheet_id=fid,name='HEATER')
            report['server']=session.info['serverInfo'];report['status']='PASSED'
    except Exception as exc:
        report['error']=str(exc)
    path=ROOT/'runtime/dwsim-smoke.json';path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=True,indent=2))
    return 0 if report['status']=='PASSED' else 1

if __name__=='__main__':raise SystemExit(run())

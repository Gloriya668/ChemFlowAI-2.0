REFERENCE_BASIS='参考依据：热力学模型适用条件与本项目工艺实例；实验文献见关联链接。'
def models(p):
    pdh=p['dataset']=='pdh';custom=p['dataset']=='custom'
    # Named methods are selection candidates; only the documented P–T correlation is implemented here.
    entries=[
      ('PR','状态方程','烃类、轻气体和 C3 分离的优先候选','含氢交互参数及近沸分离精度须按温压范围核验。'),
      ('SRK','状态方程','烃类与富氢体系，可与 PR 对照','临界区与相对挥发度需要实验对照。'),
      ('PR-BM','状态方程','适用于 C3 分离、油气和燃烧体系','Boston–Mathias 温度函数及 BIP 需核实。'),
      ('RKS-BM','状态方程','用于烃分离和油气体系候选','需确认温度函数、组分常数和适用温压。'),
      ('LK-PLOCK','状态方程','炼油、非极性烃混合物候选','强极性体系和含氢混合物需额外验证。'),
      ('NRTL','活度系数','中低压、极性与强非理想液相，可描述 VLE/LLE','需要可靠二元参数及合适气相模型；不直接外推到高压。'),
      ('UNIQUAC','活度系数','极性、多组分以及液液分相的比较模型','需分子结构参数和二元交互参数。'),
      ('WILSON','活度系数','互溶非理想液相和共沸分离候选','常规 Wilson 不能描述液液分相，存在分相器时不优先。'),
      ('NRTL-HOC','活度系数','NRTL 液相与 HOC 气相缔合修正组合','只有存在气相缔合证据时选用；不能凭非理想性自动判定。'),
      ('NRTL-RK','活度系数','NRTL 液相与 RK 气相逸度组合','需要验证压力范围与二元参数。'),
      ('UNIFAC','预测方法','缺少实验参数时用于前期筛查','依赖基团映射；预测不能当作实验验证。'),
      ('UNIF-DMD','预测方法','修正 UNIFAC（Dortmund），用于温度相关预测','需完整官能团及组间参数。'),
      ('PSRK','预测状态方程','用于石化 VLE 和化学体系预测方法','需有效基团参数；轻气体处理须检查。'),
      ('PRWS','混合规则','PR 与 Wong–Sandler 混合规则，用于非理想体系','不能直接套用普通 PR 的 kij；需相应参数回归。'),
      ('PRMHV2','混合规则','PR 与 MHV2 超额自由能混合规则','需活度系数参数；高压外推须实验验证。'),
      ('RKSWS','混合规则','SRK 与 Wong–Sandler 混合规则','需与该混合规则一致的参数。'),
      ('SR-POLAR','状态方程','适用于高压极性体系候选','需要纯组分和交叉参数，当前未接入求解。'),
      ('ELECNRTL','电解质','电解质、酸碱及离子反应体系','必须定义离子、平衡反应与电解质参数。'),
      ('PC-SAFT','分子状态方程','高聚物体系候选，也需组分特征参数','需链段、能量和缔合参数，不默认适合当前体系。'),
      ('STEAMNBS','水和蒸汽','用于纯水蒸汽系统方法','专用于水/蒸汽，不用于整个有机混合物。'),
    ]
    rec=None if custom else 'PR' if pdh else 'NRTL'
    order=['PR','SRK','PR-BM','RKS-BM','PRWS'] if pdh else ['NRTL','UNIQUAC','NRTL-RK','UNIFAC','WILSON']
    entries.sort(key=lambda x:order.index(x[0]) if x[0] in order else 99)
    return [{'id':i,'family':f,'reason':r,'risk':k,'recommended':i==rec,'source_name':REFERENCE_BASIS,'source_type':'RULE','status':'NEEDS_HUMAN_REVIEW','evidence':(['工艺适用性：烃分离/C3 分离推荐 PR、SRK、PR-BM、RKS-BM。','本项目包含丙烷、丙烯和氢气，优先评估状态方程。'] if pdh else ['工艺适用性：液液分相及极性化学体系推荐 NRTL、UNIQUAC。','本项目吡啶工艺实例采用 NRTL，且有水/有机物非理想性。']) if i==rec else [],'url':'https://trc.nist.gov/ThermoML/10.1016/j.fluid.2006.03.009.html' if pdh else None} for i,f,r,k in entries]

export type CampusPreset='overview'|'top'|'process'|'tanks';
export type CampusRoute='none'|'fire'|'escape';
export const campusZones=[
 {id:'production',name:'生产装置区',color:'#65d7dc',description:'参考图中的四组生产车间，展示设备框架、塔器和架空管线。',points:['设备检修与吊装空间','生产区与储运区的接口','管廊走向及公用工程连接']},
 {id:'storage',name:'储罐与装卸区',color:'#f2bd72',description:'集中展示立式储罐、围堰、泵区和事故收集设施的空间关系。',points:['介质相容性与罐组分区','围堰、排水及事故收集','车辆装卸与人员通道']},
 {id:'utilities',name:'公用工程与环保区',color:'#7ebde9',description:'展示循环水、消防水、配电及水处理设施与生产区的连接。',points:['公辅供给可靠性','清污分流与收集边界','检修及扩建接口']},
 {id:'admin',name:'管理与辅助区',color:'#a49ce8',description:'参考原图布置管理、控制及辅助建筑，理解人流和物流的组织。',points:['人流与物流入口','控制与生产岗位联系','应急集合与疏散方向']},
 {id:'warehouse',name:'仓储与配套区',color:'#a5d9ac',description:'展示仓库、装卸棚与外部道路的连接。',points:['分类储存与装卸组织','车辆转弯和待装空间','与生产区的运输联系']},
 {id:'reserve',name:'预留发展区',color:'#849aa8',description:'保持相对完整的预留地，理解后续扩建与既有管廊之间的关系。',points:['扩建施工通道','管线及公辅容量预留','避免新增装置切断既有道路']},
];

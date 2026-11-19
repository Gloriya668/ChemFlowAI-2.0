export type Kind = 'feed'|'product'|'mixer'|'splitter'|'drum'|'column'|'divided'|'reactor'|'plug'|'exchanger'|'multiheat'|'compressor'|'multicompressor'|'pump'|'valve'|'train';
export type Evidence={id:string;title:string;url:string;abstract:string;authors:string;year:string;provider:string;journal?:string};
export type DeviceDetails={principle:string;internals:string;parameters:{name:string;unit:string;meaning:string;watch:string}[]};
export type Equipment = {id:string;name:string;module:string;role:string;group?:string;details?:DeviceDetails};
export type FlowNode = Equipment & {kind:Kind;x:number;y:number;labelOffset?:number[]};
export type FlowEdge = {from:string;to:string;label:string;tone?:'recycle'|'product'|'heat';sp?:string;tp?:string;via?:number[][];labelAt?:number[]};
export type LearningCase = {custom?:boolean;revision?:number;sources?:Evidence[];updatedAt?:string;id:string;title:string;category:string;level:string;section:string;example:string;pages:string;figures:string;summary:string;method:string;points:string[];note?:string;width:number;height:number;nodes:FlowNode[];edges:FlowEdge[];equipment?:Equipment[];detail?:{width:number;height:number;nodes:FlowNode[];edges:FlowEdge[]}};

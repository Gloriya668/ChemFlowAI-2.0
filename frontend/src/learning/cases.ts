import type {LearningCase} from './types';
export const learningCases:LearningCase[] = [
  {
    "id": "hydrocarbon-mixing",
    "title": "三股烃类物流混合",
    "category": "基础分离",
    "level": "入门",
    "section": "4.1.1",
    "example": "4.1",
    "pages": "131–132",
    "figures": "4-3",
    "summary": "从最简单的混合单元开始，认识多股进料与一股出口的连接。",
    "method": "CHAO-SEA",
    "points": [
      "识别物流与设备",
      "建立多入口单出口结构",
      "理解混合物料衡算"
    ],
    "width": 1200,
    "height": 580,
    "nodes": [
      {
        "id": "FEED1",
        "name": "烃类进料 1",
        "kind": "feed",
        "x": 155,
        "y": 150,
        "module": "",
        "role": ""
      },
      {
        "id": "FEED2",
        "name": "烃类进料 2",
        "kind": "feed",
        "x": 155,
        "y": 290,
        "module": "",
        "role": ""
      },
      {
        "id": "FEED3",
        "name": "烃类进料 3",
        "kind": "feed",
        "x": 155,
        "y": 430,
        "module": "",
        "role": ""
      },
      {
        "id": "MIXER",
        "name": "混合器",
        "kind": "mixer",
        "x": 580,
        "y": 290,
        "module": "Mixer",
        "role": "汇合三股含丙烷、正丁烷、正戊烷和正己烷的进料。"
      },
      {
        "id": "OUT",
        "name": "混合物流",
        "kind": "product",
        "x": 1010,
        "y": 290,
        "module": "",
        "role": ""
      }
    ],
    "edges": [
      {
        "to": "MIXER",
        "label": "",
        "sp": "R",
        "tp": "T",
        "from": "FEED1",
        "via": [
          [
            580,
            150
          ]
        ]
      },
      {
        "to": "MIXER",
        "label": "",
        "sp": "R",
        "tp": "L",
        "from": "FEED2"
      },
      {
        "to": "MIXER",
        "label": "",
        "sp": "R",
        "tp": "B",
        "from": "FEED3",
        "via": [
          [
            580,
            430
          ]
        ]
      },
      {
        "to": "OUT",
        "label": "混合后物流",
        "sp": "R",
        "tp": "L",
        "from": "MIXER",
        "tone": "product"
      }
    ]
  },
  {
    "id": "two-stage-flash",
    "title": "两级闪蒸分离",
    "category": "基础分离",
    "level": "入门",
    "section": "4.3.1",
    "example": "4.5",
    "pages": "139–140",
    "figures": "4-20",
    "summary": "把一次闪蒸的液相送往下一闪蒸器，观察逐级分离的结构。",
    "method": "PENG-ROB",
    "points": [
      "识别汽液出口",
      "追踪级间液相",
      "理解分离条件影响相态"
    ],
    "width": 1200,
    "height": 580,
    "nodes": [
      {
        "id": "FEED",
        "name": "氢气 / 烃类进料",
        "kind": "feed",
        "x": 120,
        "y": 320,
        "module": "",
        "role": ""
      },
      {
        "id": "FLASH1",
        "name": "一级闪蒸器",
        "kind": "drum",
        "x": 390,
        "y": 320,
        "module": "Flash2",
        "role": "第一步汽液分离，液相送入第二级。"
      },
      {
        "id": "FLASH2",
        "name": "二级闪蒸器",
        "kind": "drum",
        "x": 760,
        "y": 320,
        "module": "Flash2",
        "role": "处理一级液相，再次得到汽相与液相。"
      },
      {
        "id": "V1",
        "name": "一级汽相",
        "kind": "product",
        "x": 390,
        "y": 125,
        "module": "",
        "role": ""
      },
      {
        "id": "V2",
        "name": "二级汽相",
        "kind": "product",
        "x": 760,
        "y": 125,
        "module": "",
        "role": ""
      },
      {
        "id": "L2",
        "name": "二级液相",
        "kind": "product",
        "x": 1060,
        "y": 320,
        "module": "",
        "role": ""
      }
    ],
    "edges": [
      {
        "to": "FLASH1",
        "label": "",
        "sp": "R",
        "tp": "L",
        "from": "FEED"
      },
      {
        "to": "V1",
        "label": "汽相",
        "sp": "T",
        "tp": "B",
        "from": "FLASH1",
        "tone": "product"
      },
      {
        "to": "FLASH2",
        "label": "一级液相",
        "sp": "R",
        "tp": "L",
        "from": "FLASH1"
      },
      {
        "to": "V2",
        "label": "汽相",
        "sp": "T",
        "tp": "B",
        "from": "FLASH2",
        "tone": "product"
      },
      {
        "to": "L2",
        "label": "液相",
        "sp": "R",
        "tp": "L",
        "from": "FLASH2",
        "tone": "product"
      }
    ]
  },
  {
    "id": "liquid-decanting",
    "title": "乙醇—甲苯—水液液分相",
    "category": "基础分离",
    "level": "入门",
    "section": "4.3.3",
    "example": "4.7",
    "pages": "142–143",
    "figures": "4-29",
    "summary": "在液液分相器内区分两种液相，认识相平衡与组分分配。",
    "method": "UNIQUAC",
    "points": [
      "区分液液与汽液分离",
      "追踪两股进料",
      "认识液相组分分配"
    ],
    "width": 1200,
    "height": 580,
    "nodes": [
      {
        "id": "FEED1",
        "name": "乙醇 / 甲苯",
        "kind": "feed",
        "x": 160,
        "y": 220,
        "module": "",
        "role": ""
      },
      {
        "id": "FEED2",
        "name": "水",
        "kind": "feed",
        "x": 160,
        "y": 400,
        "module": "",
        "role": ""
      },
      {
        "id": "DECANTER",
        "name": "液液分相器",
        "kind": "drum",
        "x": 570,
        "y": 310,
        "module": "Decanter",
        "role": "在液液平衡条件下形成两股不同组成的液相。"
      },
      {
        "id": "L1",
        "name": "液相一",
        "kind": "product",
        "x": 1030,
        "y": 210,
        "module": "",
        "role": ""
      },
      {
        "id": "L2",
        "name": "液相二",
        "kind": "product",
        "x": 1030,
        "y": 410,
        "module": "",
        "role": ""
      }
    ],
    "edges": [
      {
        "to": "DECANTER",
        "label": "",
        "sp": "R",
        "tp": "L-25",
        "from": "FEED1"
      },
      {
        "to": "DECANTER",
        "label": "",
        "sp": "R",
        "tp": "L25",
        "from": "FEED2"
      },
      {
        "to": "L1",
        "label": "分相出口",
        "sp": "R-25",
        "tp": "L",
        "from": "DECANTER",
        "tone": "product"
      },
      {
        "to": "L2",
        "label": "分相出口",
        "sp": "R25",
        "tp": "L",
        "from": "DECANTER",
        "tone": "product"
      }
    ]
  },
  {
    "id": "multistage-compression",
    "title": "多级压缩与级间冷却",
    "category": "输送换热",
    "level": "入门",
    "section": "5.4",
    "example": "5.4",
    "pages": "156–157",
    "figures": "5-18",
    "summary": "通过一个多级压缩模块，认识压缩和级间冷却的组合。",
    "method": "PENG-ROB",
    "points": [
      "辨认压缩机功能",
      "认识级间冷却",
      "区分模块与内部设备"
    ],
    "width": 1200,
    "height": 580,
    "nodes": [
      {
        "id": "FEED",
        "name": "气体进料",
        "kind": "feed",
        "x": 170,
        "y": 290,
        "module": "",
        "role": ""
      },
      {
        "id": "MCOMPR",
        "name": "多级压缩机",
        "kind": "multicompressor",
        "x": 600,
        "y": 290,
        "module": "MCompr",
        "role": "包含两级压缩及级间冷却，统一描述升压过程。"
      },
      {
        "id": "PROD",
        "name": "压缩后气体",
        "kind": "product",
        "x": 1030,
        "y": 290,
        "module": "",
        "role": ""
      }
    ],
    "edges": [
      {
        "to": "MCOMPR",
        "label": "气体",
        "sp": "R",
        "tp": "L",
        "from": "FEED"
      },
      {
        "to": "PROD",
        "label": "升压出口",
        "sp": "R",
        "tp": "L",
        "from": "MCOMPR",
        "tone": "product"
      }
    ],
    "note": "MCOMPR 为一个 MCompr 模块；图内双压缩符号与冷却段表示模块内部结构。"
  },
  {
    "id": "two-stream-heat-exchange",
    "title": "两股物流换热",
    "category": "输送换热",
    "level": "入门",
    "section": "6.3",
    "example": "6.4",
    "pages": "181–183",
    "figures": "6-27",
    "summary": "冷热两股物流在换热器中传递热量，物料保持各自独立。",
    "method": "PENG-ROB",
    "points": [
      "分辨冷热侧",
      "热量交换与物料混合的区别",
      "辨认换热器进出口"
    ],
    "width": 1200,
    "height": 580,
    "nodes": [
      {
        "id": "HOT-IN",
        "name": "热侧 · 苯",
        "kind": "feed",
        "x": 170,
        "y": 200,
        "module": "",
        "role": ""
      },
      {
        "id": "COLD-IN",
        "name": "冷侧 · 正十二烷",
        "kind": "feed",
        "x": 170,
        "y": 400,
        "module": "",
        "role": ""
      },
      {
        "id": "HEX",
        "name": "两物流换热器",
        "kind": "exchanger",
        "x": 600,
        "y": 300,
        "module": "HeatX",
        "role": "两侧物流间传热；冷热侧没有物料交叉混合。"
      },
      {
        "id": "HOT-OUT",
        "name": "热侧出口",
        "kind": "product",
        "x": 1030,
        "y": 200,
        "module": "",
        "role": ""
      },
      {
        "id": "COLD-OUT",
        "name": "冷侧出口",
        "kind": "product",
        "x": 1030,
        "y": 400,
        "module": "",
        "role": ""
      }
    ],
    "edges": [
      {
        "to": "HEX",
        "label": "热侧入口",
        "sp": "R",
        "tp": "L-22",
        "from": "HOT-IN"
      },
      {
        "to": "HOT-OUT",
        "label": "热侧出口",
        "sp": "R-22",
        "tp": "L",
        "from": "HEX",
        "tone": "product"
      },
      {
        "to": "HEX",
        "label": "冷侧入口",
        "sp": "R",
        "tp": "L22",
        "from": "COLD-IN"
      },
      {
        "to": "COLD-OUT",
        "label": "冷侧出口",
        "sp": "R22",
        "tp": "L",
        "from": "HEX",
        "tone": "product"
      }
    ]
  },
  {
    "id": "multistream-heat-exchange",
    "title": "多股物流换热",
    "category": "输送换热",
    "level": "进阶",
    "section": "6.4",
    "example": "6.6",
    "pages": "194–196",
    "figures": "6-57",
    "summary": "把一股热流与两股冷流放在同一个多流换热模型中。",
    "method": "PENG-ROB",
    "points": [
      "辨认多个独立通道",
      "认识冷热负荷匹配",
      "理解多流换热模块"
    ],
    "width": 1200,
    "height": 580,
    "nodes": [
      {
        "id": "CBOX",
        "name": "多物流换热器",
        "kind": "multiheat",
        "x": 600,
        "y": 300,
        "module": "MHeatX",
        "role": "组织一股热流与两股冷流之间的热交换，保持三个物料通道独立。"
      },
      {
        "id": "IN0",
        "name": "热侧入口",
        "kind": "feed",
        "x": 160,
        "y": 170,
        "module": "",
        "role": ""
      },
      {
        "id": "OUT0",
        "name": "热侧出口",
        "kind": "product",
        "x": 1040,
        "y": 170,
        "module": "",
        "role": ""
      },
      {
        "id": "IN1",
        "name": "冷侧一入口",
        "kind": "feed",
        "x": 160,
        "y": 300,
        "module": "",
        "role": ""
      },
      {
        "id": "OUT1",
        "name": "冷侧一出口",
        "kind": "product",
        "x": 1040,
        "y": 300,
        "module": "",
        "role": ""
      },
      {
        "id": "IN2",
        "name": "冷侧二入口",
        "kind": "feed",
        "x": 160,
        "y": 430,
        "module": "",
        "role": ""
      },
      {
        "id": "OUT2",
        "name": "冷侧二出口",
        "kind": "product",
        "x": 1040,
        "y": 430,
        "module": "",
        "role": ""
      }
    ],
    "edges": [
      {
        "to": "CBOX",
        "label": "",
        "sp": "R",
        "tp": "L-42",
        "from": "IN0"
      },
      {
        "to": "OUT0",
        "label": "",
        "sp": "R-42",
        "tp": "L",
        "from": "CBOX",
        "tone": "product"
      },
      {
        "to": "CBOX",
        "label": "",
        "sp": "R",
        "tp": "L0",
        "from": "IN1"
      },
      {
        "to": "OUT1",
        "label": "",
        "sp": "R0",
        "tp": "L",
        "from": "CBOX",
        "tone": "product"
      },
      {
        "to": "CBOX",
        "label": "",
        "sp": "R",
        "tp": "L42",
        "from": "IN2"
      },
      {
        "to": "OUT2",
        "label": "",
        "sp": "R42",
        "tp": "L",
        "from": "CBOX",
        "tone": "product"
      }
    ]
  },
  {
    "id": "ethylbenzene-styrene-distillation",
    "title": "乙苯—苯乙烯精馏",
    "category": "塔器分离",
    "level": "入门",
    "section": "7.4",
    "example": "7.3",
    "pages": "206–221",
    "figures": "7-18",
    "summary": "用严格精馏塔模型，把乙苯与苯乙烯分别富集到塔顶和塔底。",
    "method": "PENG-ROB",
    "points": [
      "理解回流与再沸",
      "识别塔顶塔底产品",
      "认识严格塔模型"
    ],
    "width": 1200,
    "height": 580,
    "nodes": [
      {
        "id": "FEED",
        "name": "乙苯 / 苯乙烯",
        "kind": "feed",
        "x": 180,
        "y": 290,
        "module": "",
        "role": ""
      },
      {
        "id": "RADFRAC",
        "name": "乙苯—苯乙烯精馏塔",
        "kind": "column",
        "x": 580,
        "y": 290,
        "module": "RadFrac",
        "role": "带全凝器与釜式再沸器的严格精馏模型；原料含微量焦油，以正十七烷表征。"
      },
      {
        "id": "DIST",
        "name": "乙苯富集物流",
        "kind": "product",
        "x": 1020,
        "y": 150,
        "module": "",
        "role": ""
      },
      {
        "id": "BOTTOM",
        "name": "苯乙烯富集物流",
        "kind": "product",
        "x": 1020,
        "y": 440,
        "module": "",
        "role": ""
      }
    ],
    "edges": [
      {
        "to": "RADFRAC",
        "label": "",
        "sp": "R",
        "tp": "L",
        "from": "FEED"
      },
      {
        "to": "DIST",
        "label": "塔顶采出",
        "sp": "T",
        "tp": "L",
        "from": "RADFRAC",
        "tone": "product",
        "via": [
          [
            580,
            150
          ]
        ]
      },
      {
        "to": "BOTTOM",
        "label": "塔底采出",
        "sp": "B",
        "tp": "L",
        "from": "RADFRAC",
        "tone": "product",
        "via": [
          [
            580,
            440
          ]
        ]
      }
    ],
    "note": "冷凝器与釜式再沸器属于 RadFrac 塔内模型，设备表按一个塔模块列示。"
  },
  {
    "id": "acetone-absorption",
    "title": "水吸收空气中的丙酮",
    "category": "塔器分离",
    "level": "入门",
    "section": "7.5",
    "example": "7.4",
    "pages": "221–223",
    "figures": "7-51",
    "summary": "让含丙酮气体与水逆向接触，认识吸收塔两端的进出物流。",
    "method": "NRTL · 氮气与氧气采用 Henry 组分处理",
    "points": [
      "理解逆流接触",
      "识别吸收剂与溶质",
      "区分吸收塔与精馏塔"
    ],
    "width": 1200,
    "height": 580,
    "nodes": [
      {
        "id": "WATER",
        "name": "吸收剂 · 水",
        "kind": "feed",
        "x": 180,
        "y": 150,
        "module": "",
        "role": ""
      },
      {
        "id": "GAS",
        "name": "空气 / 丙酮",
        "kind": "feed",
        "x": 180,
        "y": 430,
        "module": "",
        "role": ""
      },
      {
        "id": "ABSORBER",
        "name": "丙酮吸收塔",
        "kind": "column",
        "x": 580,
        "y": 290,
        "module": "RadFrac",
        "role": "无冷凝器、无再沸器；水与含丙酮气体逆向接触。"
      },
      {
        "id": "CLEAN",
        "name": "净化后气体",
        "kind": "product",
        "x": 1020,
        "y": 150,
        "module": "",
        "role": ""
      },
      {
        "id": "RICH",
        "name": "含丙酮水溶液",
        "kind": "product",
        "x": 1020,
        "y": 440,
        "module": "",
        "role": ""
      }
    ],
    "edges": [
      {
        "to": "ABSORBER",
        "label": "塔上部进水",
        "sp": "R",
        "tp": "L-65",
        "from": "WATER"
      },
      {
        "to": "ABSORBER",
        "label": "塔下部进气",
        "sp": "R",
        "tp": "L65",
        "from": "GAS"
      },
      {
        "to": "CLEAN",
        "label": "塔顶气相",
        "sp": "T",
        "tp": "L",
        "from": "ABSORBER",
        "tone": "product",
        "via": [
          [
            580,
            150
          ]
        ]
      },
      {
        "to": "RICH",
        "label": "塔底液相",
        "sp": "B",
        "tp": "L",
        "from": "ABSORBER",
        "tone": "product",
        "via": [
          [
            580,
            440
          ]
        ]
      }
    ]
  },
  {
    "id": "isopropanol-extraction",
    "title": "水萃取苯溶液中的异丙醇",
    "category": "塔器分离",
    "level": "进阶",
    "section": "7.7",
    "example": "7.6",
    "pages": "232–234",
    "figures": "7-72",
    "summary": "利用异丙醇在两种液相中的分配差异完成液液萃取。",
    "method": "NRTL · 液液平衡",
    "points": [
      "认识萃取剂",
      "辨认萃余相与萃取相",
      "理解逆流液液接触"
    ],
    "width": 1200,
    "height": 580,
    "nodes": [
      {
        "id": "WATER",
        "name": "萃取剂 · 水",
        "kind": "feed",
        "x": 180,
        "y": 150,
        "module": "",
        "role": ""
      },
      {
        "id": "BEN-PROP",
        "name": "苯 / 异丙醇",
        "kind": "feed",
        "x": 180,
        "y": 430,
        "module": "",
        "role": ""
      },
      {
        "id": "EXTRACT",
        "name": "液液萃取塔",
        "kind": "column",
        "x": 580,
        "y": 290,
        "module": "Extract",
        "role": "以水作为萃取剂，从苯溶液中萃取异丙醇。"
      },
      {
        "id": "BEN",
        "name": "苯富集萃余相",
        "kind": "product",
        "x": 1020,
        "y": 150,
        "module": "",
        "role": ""
      },
      {
        "id": "WT-PROP",
        "name": "含异丙醇水相",
        "kind": "product",
        "x": 1020,
        "y": 440,
        "module": "",
        "role": ""
      }
    ],
    "edges": [
      {
        "to": "EXTRACT",
        "label": "",
        "sp": "R",
        "tp": "L-65",
        "from": "WATER"
      },
      {
        "to": "EXTRACT",
        "label": "",
        "sp": "R",
        "tp": "L65",
        "from": "BEN-PROP"
      },
      {
        "to": "BEN",
        "label": "萃余相",
        "sp": "T",
        "tp": "L",
        "from": "EXTRACT",
        "tone": "product",
        "via": [
          [
            580,
            150
          ]
        ]
      },
      {
        "to": "WT-PROP",
        "label": "萃取相",
        "sp": "B",
        "tp": "L",
        "from": "EXTRACT",
        "tone": "product",
        "via": [
          [
            580,
            440
          ]
        ]
      }
    ]
  },
  {
    "id": "butene-isomerization",
    "title": "丁烯异构化反应",
    "category": "反应过程",
    "level": "入门",
    "section": "8.2",
    "example": "8.1",
    "pages": "244–247",
    "figures": "8-2",
    "summary": "从反应物、产物及副反应的关系，认识化学计量反应器。",
    "method": "RK-SOAVE",
    "points": [
      "建立反应组分集合",
      "理解主副反应",
      "认识 RStoic 转化率模型"
    ],
    "width": 1200,
    "height": 580,
    "nodes": [
      {
        "id": "FEED",
        "name": "含丁烯的混合进料",
        "kind": "feed",
        "x": 170,
        "y": 290,
        "module": "",
        "role": ""
      },
      {
        "id": "RSTOIC",
        "name": "化学计量反应器",
        "kind": "reactor",
        "x": 590,
        "y": 290,
        "module": "RStoic",
        "role": "描述丁烯异构化和伴随副反应；反应式定义组分转化。"
      },
      {
        "id": "PROD",
        "name": "异构化反应产物",
        "kind": "product",
        "x": 1030,
        "y": 290,
        "module": "",
        "role": ""
      }
    ],
    "edges": [
      {
        "to": "RSTOIC",
        "label": "反应进料",
        "sp": "R",
        "tp": "L",
        "from": "FEED"
      },
      {
        "to": "PROD",
        "label": "反应混合物",
        "sp": "R",
        "tp": "L",
        "from": "RSTOIC",
        "tone": "product"
      }
    ]
  },
  {
    "id": "propylene-chlorination",
    "title": "丙烯氯化平推流反应",
    "category": "反应过程",
    "level": "进阶",
    "section": "8.8",
    "example": "8.6",
    "pages": "261–263",
    "figures": "8-44",
    "summary": "先混合丙烯与氯气，再进入平推流反应器，认识动力学反应模型。",
    "method": "IDEAL",
    "points": [
      "连接混合与反应单元",
      "区分主副反应",
      "认识沿程反应模型"
    ],
    "width": 1200,
    "height": 580,
    "nodes": [
      {
        "id": "C3H6",
        "name": "丙烯",
        "kind": "feed",
        "x": 140,
        "y": 200,
        "module": "",
        "role": ""
      },
      {
        "id": "CL2",
        "name": "氯气",
        "kind": "feed",
        "x": 140,
        "y": 400,
        "module": "",
        "role": ""
      },
      {
        "id": "MIX",
        "name": "进料混合器",
        "kind": "mixer",
        "x": 440,
        "y": 300,
        "module": "Mixer",
        "role": "汇合丙烯与氯气。"
      },
      {
        "id": "RPLUG",
        "name": "平推流反应器",
        "kind": "plug",
        "x": 770,
        "y": 300,
        "module": "RPlug",
        "role": "按动力学模型描述丙烯氯化及副反应。"
      },
      {
        "id": "PROD",
        "name": "反应混合产物",
        "kind": "product",
        "x": 1060,
        "y": 300,
        "module": "",
        "role": ""
      }
    ],
    "edges": [
      {
        "to": "MIX",
        "label": "",
        "sp": "R",
        "tp": "L-18",
        "from": "C3H6"
      },
      {
        "to": "MIX",
        "label": "",
        "sp": "R",
        "tp": "L18",
        "from": "CL2"
      },
      {
        "to": "RPLUG",
        "label": "混合进料",
        "sp": "R",
        "tp": "L",
        "from": "MIX"
      },
      {
        "to": "PROD",
        "label": "",
        "sp": "R",
        "tp": "L",
        "from": "RPLUG",
        "tone": "product"
      }
    ]
  },
  {
    "id": "extractive-distillation",
    "title": "甲苯—甲基环己烷萃取精馏",
    "category": "强化精馏",
    "level": "进阶",
    "section": "10.1",
    "example": "10.1",
    "pages": "309–317",
    "figures": "10-1",
    "summary": "通过萃取精馏、溶剂再生和补充溶剂，建立完整溶剂循环。",
    "method": "UNIFAC",
    "points": [
      "理解溶剂改变相对挥发度",
      "追踪两塔产品",
      "建立溶剂回收闭环"
    ],
    "width": 1400,
    "height": 740,
    "nodes": [
      {
        "id": "FEED",
        "name": "甲苯 / 甲基环己烷",
        "kind": "feed",
        "x": 140,
        "y": 365,
        "module": "",
        "role": ""
      },
      {
        "id": "MAKEUP",
        "name": "补充苯酚",
        "kind": "feed",
        "x": 140,
        "y": 165,
        "module": "",
        "role": ""
      },
      {
        "id": "MIXER",
        "name": "溶剂混合器",
        "kind": "mixer",
        "x": 410,
        "y": 165,
        "module": "Mixer",
        "role": "混合回收苯酚与补充萃取剂。"
      },
      {
        "id": "EXT-COL",
        "name": "萃取精馏塔",
        "kind": "column",
        "x": 590,
        "y": 365,
        "module": "RadFrac",
        "role": "苯酚从塔上部加入；甲基环己烷从塔顶采出。"
      },
      {
        "id": "REGEN",
        "name": "溶剂再生塔",
        "kind": "column",
        "x": 1000,
        "y": 365,
        "module": "RadFrac",
        "role": "从塔顶回收甲苯，苯酚由塔底返回混合器。"
      },
      {
        "id": "MCH",
        "name": "甲基环己烷",
        "kind": "product",
        "x": 800,
        "y": 130,
        "module": "",
        "role": ""
      },
      {
        "id": "TOL",
        "name": "甲苯",
        "kind": "product",
        "x": 1240,
        "y": 185,
        "module": "",
        "role": ""
      }
    ],
    "edges": [
      {
        "to": "MIXER",
        "label": "",
        "sp": "R",
        "tp": "L",
        "from": "MAKEUP"
      },
      {
        "to": "EXT-COL",
        "label": "循环萃取剂",
        "sp": "R",
        "tp": "L-60",
        "from": "MIXER",
        "via": [
          [
            490,
            165
          ],
          [
            490,
            305
          ]
        ]
      },
      {
        "to": "EXT-COL",
        "label": "原料",
        "sp": "R",
        "tp": "L",
        "from": "FEED"
      },
      {
        "to": "MCH",
        "label": "塔顶",
        "sp": "T",
        "tp": "L",
        "from": "EXT-COL",
        "tone": "product",
        "via": [
          [
            590,
            130
          ]
        ]
      },
      {
        "to": "REGEN",
        "label": "甲苯 / 苯酚",
        "sp": "B",
        "tp": "L",
        "from": "EXT-COL",
        "via": [
          [
            590,
            535
          ],
          [
            830,
            535
          ],
          [
            830,
            365
          ]
        ]
      },
      {
        "to": "TOL",
        "label": "塔顶",
        "sp": "T",
        "tp": "L",
        "from": "REGEN",
        "tone": "product",
        "via": [
          [
            1000,
            185
          ]
        ]
      },
      {
        "to": "MIXER",
        "label": "苯酚回收",
        "sp": "B",
        "tp": "B",
        "from": "REGEN",
        "tone": "recycle",
        "via": [
          [
            1000,
            650
          ],
          [
            410,
            650
          ]
        ]
      }
    ]
  },
  {
    "id": "ethanol-azeotropic",
    "title": "乙醇脱水共沸精馏",
    "category": "强化精馏",
    "level": "进阶",
    "section": "10.2",
    "example": "10.2",
    "pages": "318–328",
    "figures": "10-45",
    "summary": "将共沸精馏、液液分相和溶剂回收组合起来，认识含水乙醇脱水。",
    "method": "UNIQ-RK",
    "points": [
      "认识共沸剂的作用",
      "追踪有机相回流",
      "理解双循环结构"
    ],
    "width": 1500,
    "height": 780,
    "nodes": [
      {
        "id": "FEED",
        "name": "含水乙醇",
        "kind": "feed",
        "x": 130,
        "y": 380,
        "module": "",
        "role": ""
      },
      {
        "id": "MAKEUP",
        "name": "补充环己烷",
        "kind": "feed",
        "x": 130,
        "y": 150,
        "module": "",
        "role": ""
      },
      {
        "id": "MXSOLV",
        "name": "共沸剂混合器",
        "kind": "mixer",
        "x": 390,
        "y": 150,
        "module": "Mixer",
        "role": "混合补充环己烷与分相器回收的有机相。"
      },
      {
        "id": "COL-MAIN",
        "name": "共沸精馏塔",
        "kind": "column",
        "x": 570,
        "y": 380,
        "module": "RadFrac",
        "role": "塔底采出乙醇；塔顶冷凝物流送往分相器。"
      },
      {
        "id": "DECANTER",
        "name": "液液分相器",
        "kind": "drum",
        "x": 890,
        "y": 160,
        "module": "Decanter",
        "role": "有机相回收共沸剂，另一液相送入溶剂回收塔。",
        "labelOffset": [
          65,
          -140
        ]
      },
      {
        "id": "COL-REC",
        "name": "溶剂回收塔",
        "kind": "column",
        "x": 1170,
        "y": 380,
        "module": "RadFrac",
        "role": "塔底排出水，塔顶物流返回主塔。"
      },
      {
        "id": "ETOH",
        "name": "乙醇产品",
        "kind": "product",
        "x": 760,
        "y": 650,
        "module": "",
        "role": ""
      },
      {
        "id": "H2O",
        "name": "水相出口",
        "kind": "product",
        "x": 1370,
        "y": 570,
        "module": "",
        "role": ""
      }
    ],
    "edges": [
      {
        "to": "MXSOLV",
        "label": "",
        "sp": "R",
        "tp": "L",
        "from": "MAKEUP"
      },
      {
        "to": "COL-MAIN",
        "label": "共沸剂",
        "sp": "R",
        "tp": "L-65",
        "from": "MXSOLV",
        "via": [
          [
            480,
            150
          ],
          [
            480,
            315
          ]
        ]
      },
      {
        "to": "COL-MAIN",
        "label": "原料",
        "sp": "R",
        "tp": "L",
        "from": "FEED"
      },
      {
        "to": "DECANTER",
        "label": "塔顶冷凝液",
        "sp": "T",
        "tp": "L",
        "from": "COL-MAIN",
        "via": [
          [
            570,
            160
          ]
        ]
      },
      {
        "to": "MXSOLV",
        "label": "有机相循环",
        "sp": "T",
        "tp": "T",
        "from": "DECANTER",
        "tone": "recycle",
        "via": [
          [
            890,
            55
          ],
          [
            390,
            55
          ]
        ]
      },
      {
        "to": "COL-REC",
        "label": "水相送回收",
        "sp": "R",
        "tp": "L",
        "from": "DECANTER",
        "via": [
          [
            1060,
            160
          ],
          [
            1060,
            380
          ]
        ]
      },
      {
        "to": "COL-MAIN",
        "label": "回收塔顶物流",
        "sp": "T",
        "tp": "R50",
        "from": "COL-REC",
        "tone": "recycle",
        "via": [
          [
            1170,
            245
          ],
          [
            750,
            245
          ],
          [
            750,
            430
          ]
        ]
      },
      {
        "to": "ETOH",
        "label": "塔底",
        "sp": "B",
        "tp": "L",
        "from": "COL-MAIN",
        "tone": "product",
        "via": [
          [
            570,
            650
          ]
        ]
      },
      {
        "to": "H2O",
        "label": "塔底",
        "sp": "B",
        "tp": "L",
        "from": "COL-REC",
        "tone": "product",
        "via": [
          [
            1170,
            570
          ]
        ]
      }
    ]
  },
  {
    "id": "thf-pressure-swing",
    "title": "四氢呋喃—水变压精馏",
    "category": "强化精馏",
    "level": "进阶",
    "section": "10.3",
    "example": "10.3",
    "pages": "330–332",
    "figures": "10-51",
    "summary": "用不同压力的两座塔配合循环，分离四氢呋喃与水。",
    "method": "NRTL-RK",
    "points": [
      "认识压力对共沸的影响",
      "辨认塔间升压泵",
      "追踪高压塔顶循环"
    ],
    "width": 1400,
    "height": 700,
    "nodes": [
      {
        "id": "FEED",
        "name": "四氢呋喃 / 水",
        "kind": "feed",
        "x": 120,
        "y": 330,
        "module": "",
        "role": ""
      },
      {
        "id": "MIX",
        "name": "循环混合器",
        "kind": "mixer",
        "x": 360,
        "y": 330,
        "module": "Mixer",
        "role": "汇合新鲜进料与高压塔顶循环物流。"
      },
      {
        "id": "LP",
        "name": "低压精馏塔",
        "kind": "column",
        "x": 630,
        "y": 330,
        "module": "RadFrac",
        "role": "塔底采出水，塔顶物流送往高压塔。"
      },
      {
        "id": "P",
        "name": "塔间输送泵",
        "kind": "pump",
        "x": 870,
        "y": 190,
        "module": "Pump",
        "role": "提升低压塔顶液体压力，送入高压塔。"
      },
      {
        "id": "HP",
        "name": "高压精馏塔",
        "kind": "column",
        "x": 1120,
        "y": 330,
        "module": "RadFrac",
        "role": "塔底采出四氢呋喃，塔顶返回前端。"
      },
      {
        "id": "B1",
        "name": "水相出口",
        "kind": "product",
        "x": 630,
        "y": 580,
        "module": "",
        "role": ""
      },
      {
        "id": "B2",
        "name": "四氢呋喃产品",
        "kind": "product",
        "x": 1120,
        "y": 580,
        "module": "",
        "role": ""
      }
    ],
    "edges": [
      {
        "to": "MIX",
        "label": "",
        "sp": "R",
        "tp": "L",
        "from": "FEED"
      },
      {
        "to": "LP",
        "label": "",
        "sp": "R",
        "tp": "L",
        "from": "MIX"
      },
      {
        "to": "P",
        "label": "低压塔顶",
        "sp": "T",
        "tp": "L",
        "from": "LP",
        "via": [
          [
            630,
            190
          ]
        ]
      },
      {
        "to": "HP",
        "label": "升压进料",
        "sp": "R",
        "tp": "L",
        "from": "P",
        "via": [
          [
            1000,
            190
          ],
          [
            1000,
            330
          ]
        ]
      },
      {
        "to": "MIX",
        "label": "高压塔顶循环",
        "sp": "T",
        "tp": "T",
        "from": "HP",
        "tone": "recycle",
        "via": [
          [
            1120,
            65
          ],
          [
            360,
            65
          ]
        ]
      },
      {
        "to": "B1",
        "label": "塔底",
        "sp": "B",
        "tp": "T",
        "from": "LP",
        "tone": "product"
      },
      {
        "to": "B2",
        "label": "塔底",
        "sp": "B",
        "tp": "T",
        "from": "HP",
        "tone": "product"
      }
    ]
  },
  {
    "id": "ethyl-acetate-reactive",
    "title": "乙酸乙酯反应精馏",
    "category": "强化精馏",
    "level": "进阶",
    "section": "10.4",
    "example": "10.4",
    "pages": "334–340",
    "figures": "10-58",
    "summary": "在同一座塔内组织酯化反应和分离，观察反应与分离的耦合。",
    "method": "NRTL-HOC",
    "points": [
      "定义酯化可逆反应",
      "认识塔内反应区",
      "区分产品物流与纯物质"
    ],
    "width": 1200,
    "height": 580,
    "nodes": [
      {
        "id": "FEED",
        "name": "乙酸 / 乙醇",
        "kind": "feed",
        "x": 180,
        "y": 290,
        "module": "",
        "role": ""
      },
      {
        "id": "RD",
        "name": "反应精馏塔",
        "kind": "column",
        "x": 580,
        "y": 290,
        "module": "RadFrac + REAC-DIST",
        "role": "在塔内定义乙酸与乙醇的可逆酯化反应，同时进行汽液分离。"
      },
      {
        "id": "DIST",
        "name": "塔顶混合物流",
        "kind": "product",
        "x": 1020,
        "y": 150,
        "module": "",
        "role": ""
      },
      {
        "id": "BOTTOM",
        "name": "塔底混合物流",
        "kind": "product",
        "x": 1020,
        "y": 440,
        "module": "",
        "role": ""
      }
    ],
    "edges": [
      {
        "to": "RD",
        "label": "反应物",
        "sp": "R",
        "tp": "L",
        "from": "FEED"
      },
      {
        "to": "DIST",
        "label": "塔顶采出",
        "sp": "T",
        "tp": "L",
        "from": "RD",
        "tone": "product",
        "via": [
          [
            580,
            150
          ]
        ]
      },
      {
        "to": "BOTTOM",
        "label": "塔底采出",
        "sp": "B",
        "tp": "L",
        "from": "RD",
        "tone": "product",
        "via": [
          [
            580,
            440
          ]
        ]
      }
    ],
    "note": "塔顶与塔底均为混合物流；本示意不宣称产品纯度或反应转化结果。"
  },
  {
    "id": "methanol-double-effect",
    "title": "甲醇—水双效精馏",
    "category": "强化精馏",
    "level": "综合",
    "section": "10.6",
    "example": "10.6",
    "pages": "348–356",
    "figures": "10-98",
    "summary": "通过换热器把高压塔的冷凝过程与低压塔的再沸过程连接起来。",
    "method": "NRTL",
    "points": [
      "识别冷热侧物料通路",
      "区分塔间物流与热集成",
      "追踪回流及再沸支路"
    ],
    "width": 1600,
    "height": 900,
    "nodes": [
      {
        "id": "FEED",
        "name": "甲醇 / 水",
        "kind": "feed",
        "x": 120,
        "y": 340,
        "module": "",
        "role": ""
      },
      {
        "id": "C1",
        "name": "低压精馏塔",
        "kind": "column",
        "x": 380,
        "y": 340,
        "module": "RadFrac",
        "role": "保留塔顶冷凝，塔底液体经外部换热器形成再沸循环。"
      },
      {
        "id": "HX",
        "name": "热耦合换热器",
        "kind": "exchanger",
        "x": 800,
        "y": 540,
        "module": "HeatX",
        "role": "高压塔顶蒸汽在热侧冷凝，为低压塔底循环液提供热量。"
      },
      {
        "id": "FS1",
        "name": "低压塔底分流器",
        "kind": "splitter",
        "x": 390,
        "y": 690,
        "module": "FSplit",
        "role": "分出再沸循环支路和送往高压塔的支路。"
      },
      {
        "id": "PUMP",
        "name": "塔间输送泵",
        "kind": "pump",
        "x": 900,
        "y": 760,
        "module": "Pump",
        "role": "把低压塔底采出液送入高压塔。"
      },
      {
        "id": "C2",
        "name": "高压精馏塔",
        "kind": "column",
        "x": 1230,
        "y": 340,
        "module": "RadFrac",
        "role": "塔顶蒸汽经 HX 冷凝后分流为产品及回流；塔底采出水。"
      },
      {
        "id": "FS2",
        "name": "高压塔顶分流器",
        "kind": "splitter",
        "x": 980,
        "y": 140,
        "module": "FSplit",
        "role": "将换热后冷凝液分成高压塔回流与甲醇产品。"
      },
      {
        "id": "DIST1",
        "name": "低压塔甲醇产品",
        "kind": "product",
        "x": 600,
        "y": 140,
        "module": "",
        "role": ""
      },
      {
        "id": "DIST2",
        "name": "高压塔甲醇产品",
        "kind": "product",
        "x": 1280,
        "y": 95,
        "module": "",
        "role": ""
      },
      {
        "id": "BOT2",
        "name": "水相出口",
        "kind": "product",
        "x": 1450,
        "y": 620,
        "module": "",
        "role": ""
      }
    ],
    "edges": [
      {
        "to": "C1",
        "label": "",
        "sp": "R",
        "tp": "L",
        "from": "FEED"
      },
      {
        "to": "DIST1",
        "label": "塔顶",
        "sp": "T",
        "tp": "L",
        "from": "C1",
        "tone": "product",
        "via": [
          [
            380,
            140
          ]
        ]
      },
      {
        "to": "FS1",
        "label": "塔底液",
        "sp": "B",
        "tp": "T",
        "from": "C1"
      },
      {
        "to": "HX",
        "label": "再沸循环",
        "sp": "R",
        "tp": "L22",
        "from": "FS1",
        "via": [
          [
            630,
            690
          ],
          [
            630,
            562
          ]
        ]
      },
      {
        "to": "C1",
        "label": "返塔汽液",
        "sp": "R22",
        "tp": "R65",
        "from": "HX",
        "tone": "recycle",
        "via": [
          [
            920,
            562
          ],
          [
            920,
            435
          ],
          [
            500,
            435
          ],
          [
            500,
            405
          ]
        ]
      },
      {
        "to": "PUMP",
        "label": "塔间液体",
        "sp": "B",
        "tp": "L",
        "from": "FS1",
        "via": [
          [
            390,
            760
          ]
        ]
      },
      {
        "to": "C2",
        "label": "高压进料",
        "sp": "R",
        "tp": "R55",
        "from": "PUMP",
        "via": [
          [
            1350,
            760
          ],
          [
            1350,
            395
          ]
        ]
      },
      {
        "to": "HX",
        "label": "热侧蒸汽",
        "sp": "T",
        "tp": "R-22",
        "from": "C2",
        "via": [
          [
            1230,
            200
          ],
          [
            1100,
            200
          ],
          [
            1100,
            518
          ]
        ]
      },
      {
        "to": "FS2",
        "label": "热侧冷凝液",
        "sp": "L-22",
        "tp": "L",
        "from": "HX",
        "via": [
          [
            690,
            518
          ],
          [
            690,
            265
          ],
          [
            820,
            265
          ],
          [
            820,
            140
          ]
        ]
      },
      {
        "to": "DIST2",
        "label": "甲醇",
        "sp": "R",
        "tp": "L",
        "from": "FS2",
        "tone": "product",
        "via": [
          [
            1100,
            140
          ],
          [
            1100,
            95
          ]
        ]
      },
      {
        "to": "C2",
        "label": "塔顶回流",
        "sp": "B",
        "tp": "L-65",
        "from": "FS2",
        "tone": "recycle",
        "via": [
          [
            980,
            275
          ]
        ]
      },
      {
        "to": "BOT2",
        "label": "塔底水",
        "sp": "B",
        "tp": "L",
        "from": "C2",
        "tone": "product",
        "via": [
          [
            1230,
            620
          ]
        ]
      }
    ],
    "note": "采用换热器与分流器组合结构；两塔热耦合发生在 HX 内，冷热侧物料不混合。"
  },
  {
    "id": "dividing-wall-column",
    "title": "苯—甲苯—邻二甲苯隔壁塔",
    "category": "强化精馏",
    "level": "进阶",
    "section": "10.7",
    "example": "10.7",
    "pages": "358–366",
    "figures": "10-121",
    "summary": "在一座隔壁塔内完成预分馏与主分离，得到三股产品。",
    "method": "SRKM",
    "points": [
      "认识塔内隔壁",
      "辨认侧线采出",
      "理解预分馏与主塔耦合"
    ],
    "width": 1200,
    "height": 580,
    "nodes": [
      {
        "id": "FEED",
        "name": "苯 / 甲苯 / 邻二甲苯",
        "kind": "feed",
        "x": 180,
        "y": 290,
        "module": "",
        "role": ""
      },
      {
        "id": "DWC",
        "name": "隔壁精馏塔",
        "kind": "divided",
        "x": 580,
        "y": 290,
        "module": "MultiFrac",
        "role": "一个模块含主塔与预分馏段；内部汽液连接实现热与物料耦合。"
      },
      {
        "id": "DIST",
        "name": "苯富集产品",
        "kind": "product",
        "x": 1020,
        "y": 130,
        "module": "",
        "role": ""
      },
      {
        "id": "SIDE",
        "name": "甲苯富集产品",
        "kind": "product",
        "x": 1020,
        "y": 290,
        "module": "",
        "role": ""
      },
      {
        "id": "BOTTOM",
        "name": "邻二甲苯富集产品",
        "kind": "product",
        "x": 1020,
        "y": 460,
        "module": "",
        "role": ""
      }
    ],
    "edges": [
      {
        "to": "DWC",
        "label": "",
        "sp": "R",
        "tp": "L",
        "from": "FEED"
      },
      {
        "to": "DIST",
        "label": "塔顶",
        "sp": "T",
        "tp": "L",
        "from": "DWC",
        "tone": "product",
        "via": [
          [
            580,
            130
          ]
        ]
      },
      {
        "to": "SIDE",
        "label": "侧线",
        "sp": "R",
        "tp": "L",
        "from": "DWC",
        "tone": "product"
      },
      {
        "to": "BOTTOM",
        "label": "塔底",
        "sp": "B",
        "tp": "L",
        "from": "DWC",
        "tone": "product",
        "via": [
          [
            580,
            460
          ]
        ]
      }
    ],
    "note": "图示为物理隔壁塔概念。用一个 MultiFrac 模块表示主塔与预分馏段，并定义内部汽液连接。"
  },
  {
    "id": "propylene-heat-pump",
    "title": "丙烯—丙烷热泵精馏",
    "category": "强化精馏",
    "level": "综合",
    "section": "10.8",
    "example": "10.8",
    "pages": "367–376",
    "figures": "10-147",
    "summary": "压缩塔顶蒸汽，将其用作再沸器热源，再经节流和冷凝形成回流。",
    "method": "PENG-ROB",
    "points": [
      "认识蒸汽再压缩",
      "追踪再沸汽相回塔",
      "区分辅助供热与热回收"
    ],
    "width": 1750,
    "height": 900,
    "nodes": [
      {
        "id": "FEED",
        "name": "丙烯 / 丙烷",
        "kind": "feed",
        "x": 130,
        "y": 365,
        "module": "",
        "role": ""
      },
      {
        "id": "HPD",
        "name": "热泵精馏塔",
        "kind": "column",
        "x": 420,
        "y": 365,
        "module": "RadFrac",
        "role": "无内置冷凝器和再沸器，分别接入外部回流与返塔蒸汽。"
      },
      {
        "id": "COMPR",
        "name": "蒸汽压缩机",
        "kind": "compressor",
        "x": 800,
        "y": 150,
        "module": "Compr",
        "role": "压缩塔顶蒸汽，使其可作为再沸器热源。"
      },
      {
        "id": "REBOILER",
        "name": "主再沸换热器",
        "kind": "exchanger",
        "x": 800,
        "y": 520,
        "module": "HeatX",
        "role": "热侧为压缩后的塔顶蒸汽，冷侧为塔底循环液。"
      },
      {
        "id": "ASSI-REB",
        "name": "辅助再沸器",
        "kind": "exchanger",
        "x": 1110,
        "y": 542,
        "module": "Heater",
        "role": "对塔底循环液补充加热。"
      },
      {
        "id": "FLASH",
        "name": "汽液分离器",
        "kind": "drum",
        "x": 1430,
        "y": 542,
        "module": "Flash2",
        "role": "气相返回塔底，液相作为丙烷产品。"
      },
      {
        "id": "VALVE",
        "name": "节流阀",
        "kind": "valve",
        "x": 800,
        "y": 740,
        "module": "Valve",
        "role": "冷凝后塔顶物流降压。"
      },
      {
        "id": "COOLER",
        "name": "辅助冷凝器",
        "kind": "exchanger",
        "x": 480,
        "y": 740,
        "module": "Heater",
        "role": "使节流后的物流冷凝，再送往分流器。"
      },
      {
        "id": "SPLITTER",
        "name": "回流分配器",
        "kind": "splitter",
        "x": 190,
        "y": 650,
        "module": "FSplit",
        "role": "将液体分为塔顶回流和丙烯产品。"
      },
      {
        "id": "PRO-D",
        "name": "丙烯产品",
        "kind": "product",
        "x": 190,
        "y": 820,
        "module": "",
        "role": ""
      },
      {
        "id": "PRO-B",
        "name": "丙烷产品",
        "kind": "product",
        "x": 1580,
        "y": 760,
        "module": "",
        "role": ""
      }
    ],
    "edges": [
      {
        "to": "HPD",
        "label": "",
        "sp": "R",
        "tp": "L",
        "from": "FEED"
      },
      {
        "to": "COMPR",
        "label": "塔顶蒸汽",
        "sp": "T",
        "tp": "L",
        "from": "HPD",
        "via": [
          [
            420,
            150
          ]
        ]
      },
      {
        "to": "REBOILER",
        "label": "压缩蒸汽",
        "sp": "R",
        "tp": "R-22",
        "from": "COMPR",
        "via": [
          [
            980,
            150
          ],
          [
            980,
            498
          ]
        ]
      },
      {
        "to": "REBOILER",
        "label": "塔底液体",
        "sp": "B",
        "tp": "L22",
        "from": "HPD",
        "via": [
          [
            420,
            542
          ]
        ]
      },
      {
        "to": "ASSI-REB",
        "label": "受热物流",
        "sp": "R22",
        "tp": "L",
        "from": "REBOILER"
      },
      {
        "to": "FLASH",
        "label": "",
        "sp": "R",
        "tp": "L",
        "from": "ASSI-REB"
      },
      {
        "to": "HPD",
        "label": "返塔蒸汽",
        "sp": "T",
        "tp": "R55",
        "from": "FLASH",
        "tone": "recycle",
        "via": [
          [
            1430,
            420
          ]
        ]
      },
      {
        "to": "PRO-B",
        "label": "塔底液",
        "sp": "B",
        "tp": "L",
        "from": "FLASH",
        "tone": "product",
        "via": [
          [
            1430,
            760
          ]
        ]
      },
      {
        "to": "VALVE",
        "label": "热侧冷凝液",
        "sp": "L-22",
        "tp": "R",
        "from": "REBOILER",
        "via": [
          [
            650,
            498
          ],
          [
            650,
            650
          ],
          [
            980,
            650
          ],
          [
            980,
            740
          ]
        ]
      },
      {
        "to": "COOLER",
        "label": "节流后物流",
        "sp": "L",
        "tp": "R",
        "from": "VALVE"
      },
      {
        "to": "SPLITTER",
        "label": "冷凝液",
        "sp": "L",
        "tp": "R",
        "from": "COOLER",
        "via": [
          [
            320,
            740
          ],
          [
            320,
            650
          ]
        ]
      },
      {
        "to": "HPD",
        "label": "塔顶回流",
        "sp": "R-20",
        "tp": "L-65",
        "from": "SPLITTER",
        "tone": "recycle",
        "via": [
          [
            280,
            630
          ],
          [
            280,
            300
          ]
        ],
        "labelAt": [
          325,
          286
        ]
      },
      {
        "to": "PRO-D",
        "label": "产品",
        "sp": "B",
        "tp": "T",
        "from": "SPLITTER",
        "tone": "product"
      }
    ]
  },
  {
    "id": "styrene-dehydrogenation",
    "title": "乙苯催化脱氢制苯乙烯",
    "category": "综合工艺",
    "level": "综合",
    "section": "11.3",
    "example": "11.2",
    "pages": "404–412",
    "figures": "11-15",
    "summary": "把反应、闪蒸、液液分相、精馏与乙苯和水的回收串成完整工艺。",
    "method": "UNIQUAC",
    "points": [
      "从简单分离模型替换为严格模型",
      "追踪原料与水的双循环",
      "理解分段建立与收敛"
    ],
    "width": 1850,
    "height": 900,
    "nodes": [
      {
        "id": "FRESH",
        "name": "新鲜乙苯",
        "kind": "feed",
        "x": 120,
        "y": 350,
        "module": "",
        "role": ""
      },
      {
        "id": "M1",
        "name": "乙苯混合器",
        "kind": "mixer",
        "x": 350,
        "y": 350,
        "module": "Mixer",
        "role": "汇合新鲜乙苯和回收乙苯。"
      },
      {
        "id": "E1",
        "name": "乙苯加热器",
        "kind": "exchanger",
        "x": 600,
        "y": 350,
        "module": "Heater",
        "role": "加热混合后的乙苯进料。"
      },
      {
        "id": "M2",
        "name": "反应进料混合器",
        "kind": "mixer",
        "x": 850,
        "y": 350,
        "module": "Mixer",
        "role": "混合乙苯物流与水蒸气。"
      },
      {
        "id": "R1",
        "name": "脱氢反应器",
        "kind": "reactor",
        "x": 1100,
        "y": 350,
        "module": "RStoic",
        "role": "描述乙苯催化脱氢生成苯乙烯和氢气。"
      },
      {
        "id": "F1",
        "name": "闪蒸分离器",
        "kind": "drum",
        "x": 1360,
        "y": 350,
        "module": "Flash2",
        "role": "闪蒸分出富氢气相，液相送去液液分相。"
      },
      {
        "id": "D1",
        "name": "液液分相器",
        "kind": "drum",
        "x": 1360,
        "y": 650,
        "module": "Decanter",
        "role": "分离水相与有机相；水相回收至蒸汽制备。"
      },
      {
        "id": "T1",
        "name": "苯乙烯精馏塔",
        "kind": "column",
        "x": 1650,
        "y": 650,
        "module": "RadFrac",
        "role": "塔顶乙苯回收，塔底苯乙烯采出。"
      },
      {
        "id": "E3",
        "name": "乙苯回收冷却器",
        "kind": "exchanger",
        "x": 850,
        "y": 130,
        "module": "Heater",
        "role": "冷却精馏塔顶回收物流，返回乙苯混合器。"
      },
      {
        "id": "WATER",
        "name": "补充水",
        "kind": "feed",
        "x": 120,
        "y": 680,
        "module": "",
        "role": ""
      },
      {
        "id": "M3",
        "name": "水混合器",
        "kind": "mixer",
        "x": 580,
        "y": 680,
        "module": "Mixer",
        "role": "汇合回收水和补充水。"
      },
      {
        "id": "E2",
        "name": "水蒸气加热器",
        "kind": "exchanger",
        "x": 850,
        "y": 680,
        "module": "Heater",
        "role": "加热水物流，为反应进料提供蒸汽。"
      },
      {
        "id": "H2",
        "name": "富氢气体",
        "kind": "product",
        "x": 1530,
        "y": 220,
        "module": "",
        "role": ""
      },
      {
        "id": "STYRENE",
        "name": "苯乙烯产品",
        "kind": "product",
        "x": 1650,
        "y": 840,
        "module": "",
        "role": ""
      }
    ],
    "edges": [
      {
        "to": "M1",
        "label": "",
        "sp": "R",
        "tp": "L",
        "from": "FRESH"
      },
      {
        "to": "E1",
        "label": "",
        "sp": "R",
        "tp": "L",
        "from": "M1"
      },
      {
        "to": "M2",
        "label": "乙苯物流",
        "sp": "R",
        "tp": "L",
        "from": "E1"
      },
      {
        "to": "R1",
        "label": "",
        "sp": "R",
        "tp": "L",
        "from": "M2"
      },
      {
        "to": "F1",
        "label": "反应流出物",
        "sp": "R",
        "tp": "L",
        "from": "R1"
      },
      {
        "to": "H2",
        "label": "气相",
        "sp": "T",
        "tp": "L",
        "from": "F1",
        "tone": "product",
        "via": [
          [
            1360,
            220
          ]
        ]
      },
      {
        "to": "D1",
        "label": "液相",
        "sp": "B",
        "tp": "T",
        "from": "F1"
      },
      {
        "to": "T1",
        "label": "有机相",
        "sp": "R",
        "tp": "L",
        "from": "D1"
      },
      {
        "to": "STYRENE",
        "label": "塔底",
        "sp": "B",
        "tp": "T",
        "from": "T1",
        "tone": "product"
      },
      {
        "to": "E3",
        "label": "乙苯回收",
        "sp": "T",
        "tp": "R",
        "from": "T1",
        "tone": "recycle",
        "via": [
          [
            1650,
            130
          ]
        ]
      },
      {
        "to": "M1",
        "label": "回收乙苯",
        "sp": "L",
        "tp": "T",
        "from": "E3",
        "tone": "recycle",
        "via": [
          [
            350,
            130
          ]
        ]
      },
      {
        "to": "M3",
        "label": "",
        "sp": "R",
        "tp": "L",
        "from": "WATER"
      },
      {
        "to": "E2",
        "label": "",
        "sp": "R",
        "tp": "L",
        "from": "M3"
      },
      {
        "to": "M2",
        "label": "水蒸气",
        "sp": "T",
        "tp": "B",
        "from": "E2"
      },
      {
        "to": "M3",
        "label": "回收水",
        "sp": "B",
        "tp": "B",
        "from": "D1",
        "tone": "recycle",
        "via": [
          [
            1360,
            810
          ],
          [
            580,
            810
          ]
        ]
      }
    ],
    "note": "分离部分采用 Flash2、Decanter 与 RadFrac 模块，组织汽液分离、液液分相与精馏。"
  },
  {
    "id": "styrene-sidechain-alkylation",
    "title": "甲苯—甲醇侧链烷基化制苯乙烯",
    "category": "综合工艺",
    "level": "综合",
    "section": "11.4",
    "example": "11.3",
    "pages": "412–423",
    "figures": "11-56",
    "summary": "从新鲜原料制备到反应、三相分离、原料回收和产品精制，认识综合流程的组织方法。",
    "method": "PSRK；三相分离采用 UNIFAC；甲醇回收采用 WILSON",
    "points": [
      "按功能段组织复杂流程",
      "追踪甲苯与甲醇双循环",
      "辨认产品与副产物"
    ],
    "width": 1900,
    "height": 1050,
    "nodes": [
      {
        "id": "TOL",
        "name": "新鲜甲苯",
        "kind": "feed",
        "x": 130,
        "y": 280,
        "module": "",
        "role": ""
      },
      {
        "id": "MEOH",
        "name": "新鲜甲醇",
        "kind": "feed",
        "x": 130,
        "y": 430,
        "module": "",
        "role": ""
      },
      {
        "id": "PREP",
        "name": "新鲜原料制备",
        "kind": "train",
        "x": 400,
        "y": 350,
        "module": "Pump / Heater / Mixer",
        "role": "P1、E1 与 P2、E2 分别制备两股新鲜原料，M1 汇合。"
      },
      {
        "id": "MIX-PREHEAT",
        "name": "循环汇合与预热",
        "kind": "train",
        "x": 760,
        "y": 350,
        "module": "Mixer / Heater",
        "role": "M2 汇合回收物流，FH1 预热混合进料。"
      },
      {
        "id": "R1",
        "name": "侧链烷基化反应器",
        "kind": "reactor",
        "x": 1100,
        "y": 350,
        "module": "RStoic",
        "role": "甲苯与甲醇发生侧链烷基化，伴随生成乙苯等副产物。"
      },
      {
        "id": "E3",
        "name": "反应流出物冷却器",
        "kind": "exchanger",
        "x": 1400,
        "y": 350,
        "module": "Heater",
        "role": "冷却反应流出物，为三相分离准备条件。"
      },
      {
        "id": "F3",
        "name": "三相分离器",
        "kind": "drum",
        "x": 1690,
        "y": 350,
        "module": "Flash3",
        "role": "分出富氢气相、含甲醇水相和有机相。"
      },
      {
        "id": "GAS",
        "name": "富氢气体",
        "kind": "product",
        "x": 1690,
        "y": 130,
        "module": "",
        "role": ""
      },
      {
        "id": "MEOH-REC",
        "name": "甲醇回收段",
        "kind": "train",
        "x": 1200,
        "y": 620,
        "module": "Valve / Heater / RadFrac / Pump",
        "role": "V3、EC3 调整水相进料；C3 分离甲醇；P3、E4 处理回收甲醇，V4、E5 处理水出口。"
      },
      {
        "id": "TOL-REC",
        "name": "甲苯回收段",
        "kind": "train",
        "x": 1690,
        "y": 620,
        "module": "Valve / Heater / RadFrac / Pump",
        "role": "V1、EC1 处理有机相；C1 回收甲苯；P4、E-100 处理循环甲苯。"
      },
      {
        "id": "STY-PURIFY",
        "name": "苯乙烯精制段",
        "kind": "train",
        "x": 1690,
        "y": 870,
        "module": "Valve / Heater / RadFrac / Pump",
        "role": "V2、EC2 调整进料；C2 分离乙苯和苯乙烯，产品分别输送冷却。"
      },
      {
        "id": "WATER",
        "name": "水相出口",
        "kind": "product",
        "x": 900,
        "y": 780,
        "module": "",
        "role": ""
      },
      {
        "id": "EB",
        "name": "乙苯副产品",
        "kind": "product",
        "x": 1350,
        "y": 990,
        "module": "",
        "role": ""
      },
      {
        "id": "ST",
        "name": "苯乙烯产品",
        "kind": "product",
        "x": 1690,
        "y": 990,
        "module": "",
        "role": ""
      }
    ],
    "edges": [
      {
        "to": "PREP",
        "label": "",
        "sp": "R",
        "tp": "L-20",
        "from": "TOL"
      },
      {
        "to": "PREP",
        "label": "",
        "sp": "R",
        "tp": "L20",
        "from": "MEOH"
      },
      {
        "to": "MIX-PREHEAT",
        "label": "新鲜混合料",
        "sp": "R",
        "tp": "L",
        "from": "PREP"
      },
      {
        "to": "R1",
        "label": "反应进料",
        "sp": "R",
        "tp": "L",
        "from": "MIX-PREHEAT"
      },
      {
        "to": "E3",
        "label": "",
        "sp": "R",
        "tp": "L",
        "from": "R1"
      },
      {
        "to": "F3",
        "label": "",
        "sp": "R",
        "tp": "L",
        "from": "E3"
      },
      {
        "to": "GAS",
        "label": "气相",
        "sp": "T",
        "tp": "B",
        "from": "F3",
        "tone": "product"
      },
      {
        "to": "TOL-REC",
        "label": "有机相",
        "sp": "B",
        "tp": "T",
        "from": "F3"
      },
      {
        "to": "MEOH-REC",
        "label": "含甲醇水相",
        "sp": "L25",
        "tp": "T",
        "from": "F3",
        "via": [
          [
            1550,
            375
          ],
          [
            1550,
            500
          ],
          [
            1200,
            500
          ]
        ]
      },
      {
        "to": "MIX-PREHEAT",
        "label": "甲醇循环",
        "sp": "L",
        "tp": "B",
        "from": "MEOH-REC",
        "tone": "recycle",
        "via": [
          [
            760,
            620
          ]
        ]
      },
      {
        "to": "MIX-PREHEAT",
        "label": "甲苯循环",
        "sp": "R",
        "tp": "T",
        "from": "TOL-REC",
        "tone": "recycle",
        "via": [
          [
            1830,
            620
          ],
          [
            1830,
            60
          ],
          [
            760,
            60
          ]
        ]
      },
      {
        "to": "WATER",
        "label": "含水物流",
        "sp": "B",
        "tp": "R",
        "from": "MEOH-REC",
        "tone": "product",
        "via": [
          [
            1200,
            780
          ]
        ]
      },
      {
        "to": "STY-PURIFY",
        "label": "乙苯 / 苯乙烯",
        "sp": "B",
        "tp": "T",
        "from": "TOL-REC"
      },
      {
        "to": "EB",
        "label": "塔顶产品",
        "sp": "L",
        "tp": "T",
        "from": "STY-PURIFY",
        "tone": "product",
        "via": [
          [
            1350,
            870
          ]
        ]
      },
      {
        "to": "ST",
        "label": "塔底产品",
        "sp": "B",
        "tp": "T",
        "from": "STY-PURIFY",
        "tone": "product"
      }
    ],
    "note": "总览按功能段归并设备，可切换“完整设备图”逐台查看；下方表格始终列出全部设备。具体设备位号与清单对应，功能段位号用于学习导航。",
    "equipment": [
      {
        "id": "P1",
        "name": "甲苯进料泵",
        "module": "Pump",
        "role": "输送新鲜甲苯。",
        "group": "PREP"
      },
      {
        "id": "E1",
        "name": "甲苯进料加热器",
        "module": "Heater",
        "role": "加热新鲜甲苯。",
        "group": "PREP"
      },
      {
        "id": "P2",
        "name": "甲醇进料泵",
        "module": "Pump",
        "role": "输送新鲜甲醇。",
        "group": "PREP"
      },
      {
        "id": "E2",
        "name": "甲醇进料加热器",
        "module": "Heater",
        "role": "加热新鲜甲醇。",
        "group": "PREP"
      },
      {
        "id": "M1",
        "name": "新鲜原料混合器",
        "module": "Mixer",
        "role": "汇合两股新鲜原料。",
        "group": "PREP"
      },
      {
        "id": "M2",
        "name": "循环混合器",
        "module": "Mixer",
        "role": "汇合新鲜混合料与循环原料。",
        "group": "MIX-PREHEAT"
      },
      {
        "id": "FH1",
        "name": "进料加热炉",
        "module": "Heater",
        "role": "预热反应器进料。",
        "group": "MIX-PREHEAT"
      },
      {
        "id": "R1",
        "name": "侧链烷基化反应器",
        "module": "RStoic",
        "role": "描述主反应及乙苯生成副反应。",
        "group": "R1"
      },
      {
        "id": "E3",
        "name": "反应流出物冷却器",
        "module": "Heater",
        "role": "冷却反应混合物。",
        "group": "E3"
      },
      {
        "id": "F3",
        "name": "三相分离器",
        "module": "Flash3",
        "role": "分离气相、有机相和水相。",
        "group": "F3"
      },
      {
        "id": "V3",
        "name": "水相减压阀",
        "module": "Valve",
        "role": "调整水相压力。",
        "group": "MEOH-REC"
      },
      {
        "id": "EC3",
        "name": "甲醇塔进料换热器",
        "module": "Heater",
        "role": "调整甲醇回收塔的进料状态。",
        "group": "MEOH-REC"
      },
      {
        "id": "C3",
        "name": "甲醇回收塔",
        "module": "RadFrac",
        "role": "塔顶回收甲醇，塔底排出水。",
        "group": "MEOH-REC"
      },
      {
        "id": "P3",
        "name": "回收甲醇输送泵",
        "module": "Pump",
        "role": "输送回收甲醇。",
        "group": "MEOH-REC"
      },
      {
        "id": "E4",
        "name": "回收甲醇加热器",
        "module": "Heater",
        "role": "加热循环甲醇。",
        "group": "MEOH-REC"
      },
      {
        "id": "V4",
        "name": "水出口减压阀",
        "module": "Valve",
        "role": "调整甲醇塔底水流压力。",
        "group": "MEOH-REC"
      },
      {
        "id": "E5",
        "name": "水出口冷却器",
        "module": "Heater",
        "role": "冷却水出口物流。",
        "group": "MEOH-REC"
      },
      {
        "id": "V1",
        "name": "有机相减压阀",
        "module": "Valve",
        "role": "调整有机相压力。",
        "group": "TOL-REC"
      },
      {
        "id": "EC1",
        "name": "甲苯塔进料换热器",
        "module": "Heater",
        "role": "调整甲苯回收塔进料状态。",
        "group": "TOL-REC"
      },
      {
        "id": "C1",
        "name": "甲苯回收塔",
        "module": "RadFrac",
        "role": "塔顶回收甲苯，塔底送苯乙烯精制。",
        "group": "TOL-REC"
      },
      {
        "id": "P4",
        "name": "回收甲苯输送泵",
        "module": "Pump",
        "role": "输送回收甲苯。",
        "group": "TOL-REC"
      },
      {
        "id": "E-100",
        "name": "回收甲苯加热器",
        "module": "Heater",
        "role": "加热循环甲苯。",
        "group": "TOL-REC"
      },
      {
        "id": "V2",
        "name": "精制进料减压阀",
        "module": "Valve",
        "role": "调整精制进料压力。",
        "group": "STY-PURIFY"
      },
      {
        "id": "EC2",
        "name": "精制进料冷却器",
        "module": "Heater",
        "role": "调整苯乙烯塔的进料状态。",
        "group": "STY-PURIFY"
      },
      {
        "id": "C2",
        "name": "苯乙烯精馏塔",
        "module": "RadFrac",
        "role": "塔顶采出乙苯，塔底采出苯乙烯。",
        "group": "STY-PURIFY"
      },
      {
        "id": "P5",
        "name": "乙苯产品泵",
        "module": "Pump",
        "role": "输送乙苯副产品。",
        "group": "STY-PURIFY"
      },
      {
        "id": "E6",
        "name": "乙苯产品冷却器",
        "module": "Heater",
        "role": "冷却乙苯副产品。",
        "group": "STY-PURIFY"
      },
      {
        "id": "P6",
        "name": "苯乙烯产品泵",
        "module": "Pump",
        "role": "输送苯乙烯产品。",
        "group": "STY-PURIFY"
      },
      {
        "id": "E7",
        "name": "苯乙烯产品冷却器",
        "module": "Heater",
        "role": "冷却苯乙烯产品。",
        "group": "STY-PURIFY"
      }
    ],
    "detail": {
      "width": 3600,
      "height": 1620,
      "nodes": [
        {
          "id": "TOL",
          "name": "新鲜甲苯",
          "x": 120,
          "y": 300,
          "kind": "feed",
          "module": "",
          "role": ""
        },
        {
          "id": "MEOH",
          "name": "新鲜甲醇",
          "x": 120,
          "y": 550,
          "kind": "feed",
          "module": "",
          "role": ""
        },
        {
          "id": "P1",
          "name": "甲苯进料泵",
          "module": "Pump",
          "role": "输送新鲜甲苯。",
          "x": 360,
          "y": 300,
          "kind": "pump"
        },
        {
          "id": "E1",
          "name": "甲苯进料加热器",
          "module": "Heater",
          "role": "加热新鲜甲苯。",
          "x": 580,
          "y": 300,
          "kind": "exchanger"
        },
        {
          "id": "P2",
          "name": "甲醇进料泵",
          "module": "Pump",
          "role": "输送新鲜甲醇。",
          "x": 360,
          "y": 550,
          "kind": "pump"
        },
        {
          "id": "E2",
          "name": "甲醇进料加热器",
          "module": "Heater",
          "role": "加热新鲜甲醇。",
          "x": 580,
          "y": 550,
          "kind": "exchanger"
        },
        {
          "id": "M1",
          "name": "新鲜原料混合器",
          "module": "Mixer",
          "role": "汇合两股新鲜原料。",
          "x": 800,
          "y": 425,
          "kind": "mixer"
        },
        {
          "id": "M2",
          "name": "循环混合器",
          "module": "Mixer",
          "role": "汇合新鲜混合料与循环原料。",
          "x": 1050,
          "y": 425,
          "kind": "mixer"
        },
        {
          "id": "FH1",
          "name": "进料加热炉",
          "module": "Heater",
          "role": "预热反应器进料。",
          "x": 1300,
          "y": 425,
          "kind": "exchanger"
        },
        {
          "id": "R1",
          "name": "侧链烷基化反应器",
          "module": "RStoic",
          "role": "描述主反应及乙苯生成副反应。",
          "x": 1550,
          "y": 425,
          "kind": "reactor"
        },
        {
          "id": "E3",
          "name": "反应流出物冷却器",
          "module": "Heater",
          "role": "冷却反应混合物。",
          "x": 1800,
          "y": 425,
          "kind": "exchanger"
        },
        {
          "id": "F3",
          "name": "三相分离器",
          "module": "Flash3",
          "role": "分离气相、有机相和水相。",
          "x": 2050,
          "y": 425,
          "kind": "drum"
        },
        {
          "id": "V1",
          "name": "有机相减压阀",
          "module": "Valve",
          "role": "调整有机相压力。",
          "x": 2290,
          "y": 425,
          "kind": "valve"
        },
        {
          "id": "EC1",
          "name": "甲苯塔进料换热器",
          "module": "Heater",
          "role": "调整甲苯回收塔进料状态。",
          "x": 2500,
          "y": 425,
          "kind": "exchanger"
        },
        {
          "id": "C1",
          "name": "甲苯回收塔",
          "module": "RadFrac",
          "role": "塔顶回收甲苯，塔底送苯乙烯精制。",
          "x": 2750,
          "y": 425,
          "kind": "column"
        },
        {
          "id": "P4",
          "name": "回收甲苯输送泵",
          "module": "Pump",
          "role": "输送回收甲苯。",
          "x": 2460,
          "y": 150,
          "kind": "pump"
        },
        {
          "id": "E-100",
          "name": "回收甲苯加热器",
          "module": "Heater",
          "role": "加热循环甲苯。",
          "x": 1550,
          "y": 150,
          "kind": "exchanger"
        },
        {
          "id": "V3",
          "name": "水相减压阀",
          "module": "Valve",
          "role": "调整水相压力。",
          "x": 2050,
          "y": 760,
          "kind": "valve"
        },
        {
          "id": "EC3",
          "name": "甲醇塔进料换热器",
          "module": "Heater",
          "role": "调整甲醇回收塔的进料状态。",
          "x": 1800,
          "y": 760,
          "kind": "exchanger"
        },
        {
          "id": "C3",
          "name": "甲醇回收塔",
          "module": "RadFrac",
          "role": "塔顶回收甲醇，塔底排出水。",
          "x": 1500,
          "y": 900,
          "kind": "column"
        },
        {
          "id": "P3",
          "name": "回收甲醇输送泵",
          "module": "Pump",
          "role": "输送回收甲醇。",
          "x": 1200,
          "y": 650,
          "kind": "pump"
        },
        {
          "id": "E4",
          "name": "回收甲醇加热器",
          "module": "Heater",
          "role": "加热循环甲醇。",
          "x": 1050,
          "y": 800,
          "kind": "exchanger"
        },
        {
          "id": "V4",
          "name": "水出口减压阀",
          "module": "Valve",
          "role": "调整甲醇塔底水流压力。",
          "x": 1200,
          "y": 1190,
          "kind": "valve"
        },
        {
          "id": "E5",
          "name": "水出口冷却器",
          "module": "Heater",
          "role": "冷却水出口物流。",
          "x": 900,
          "y": 1190,
          "kind": "exchanger"
        },
        {
          "id": "V2",
          "name": "精制进料减压阀",
          "module": "Valve",
          "role": "调整精制进料压力。",
          "x": 2750,
          "y": 750,
          "kind": "valve"
        },
        {
          "id": "EC2",
          "name": "精制进料冷却器",
          "module": "Heater",
          "role": "调整苯乙烯塔的进料状态。",
          "x": 2470,
          "y": 970,
          "kind": "exchanger"
        },
        {
          "id": "C2",
          "name": "苯乙烯精馏塔",
          "module": "RadFrac",
          "role": "塔顶采出乙苯，塔底采出苯乙烯。",
          "x": 2750,
          "y": 1250,
          "kind": "column"
        },
        {
          "id": "P5",
          "name": "乙苯产品泵",
          "module": "Pump",
          "role": "输送乙苯副产品。",
          "x": 2990,
          "y": 1050,
          "kind": "pump"
        },
        {
          "id": "E6",
          "name": "乙苯产品冷却器",
          "module": "Heater",
          "role": "冷却乙苯副产品。",
          "x": 3200,
          "y": 1050,
          "kind": "exchanger"
        },
        {
          "id": "P6",
          "name": "苯乙烯产品泵",
          "module": "Pump",
          "role": "输送苯乙烯产品。",
          "x": 2990,
          "y": 1480,
          "kind": "pump"
        },
        {
          "id": "E7",
          "name": "苯乙烯产品冷却器",
          "module": "Heater",
          "role": "冷却苯乙烯产品。",
          "x": 3200,
          "y": 1480,
          "kind": "exchanger"
        },
        {
          "id": "GAS",
          "name": "富氢气体",
          "x": 2050,
          "y": 190,
          "kind": "product",
          "module": "",
          "role": ""
        },
        {
          "id": "WATER",
          "name": "水相出口",
          "x": 580,
          "y": 1190,
          "kind": "product",
          "module": "",
          "role": ""
        },
        {
          "id": "EB",
          "name": "乙苯副产品",
          "x": 3450,
          "y": 1050,
          "kind": "product",
          "module": "",
          "role": ""
        },
        {
          "id": "ST",
          "name": "苯乙烯产品",
          "x": 3450,
          "y": 1480,
          "kind": "product",
          "module": "",
          "role": ""
        }
      ],
      "edges": [
        {
          "from": "TOL",
          "to": "P1",
          "label": "",
          "sp": "R",
          "tp": "L"
        },
        {
          "from": "P1",
          "to": "E1",
          "label": "",
          "sp": "R",
          "tp": "L"
        },
        {
          "from": "MEOH",
          "to": "P2",
          "label": "",
          "sp": "R",
          "tp": "L"
        },
        {
          "from": "P2",
          "to": "E2",
          "label": "",
          "sp": "R",
          "tp": "L"
        },
        {
          "from": "M1",
          "to": "M2",
          "label": "",
          "sp": "R",
          "tp": "L"
        },
        {
          "from": "M2",
          "to": "FH1",
          "label": "",
          "sp": "R",
          "tp": "L"
        },
        {
          "from": "FH1",
          "to": "R1",
          "label": "",
          "sp": "R",
          "tp": "L"
        },
        {
          "from": "R1",
          "to": "E3",
          "label": "",
          "sp": "R",
          "tp": "L"
        },
        {
          "from": "E3",
          "to": "F3",
          "label": "",
          "sp": "R",
          "tp": "L"
        },
        {
          "from": "F3",
          "to": "V1",
          "label": "",
          "sp": "R",
          "tp": "L"
        },
        {
          "from": "V1",
          "to": "EC1",
          "label": "",
          "sp": "R",
          "tp": "L"
        },
        {
          "from": "EC1",
          "to": "C1",
          "label": "",
          "sp": "R",
          "tp": "L"
        },
        {
          "from": "E1",
          "to": "M1",
          "label": "甲苯",
          "sp": "R",
          "tp": "L-18"
        },
        {
          "from": "E2",
          "to": "M1",
          "label": "甲醇",
          "sp": "R",
          "tp": "L18"
        },
        {
          "from": "F3",
          "to": "GAS",
          "label": "气相",
          "sp": "T",
          "tp": "B",
          "tone": "product"
        },
        {
          "from": "C1",
          "to": "P4",
          "label": "塔顶甲苯",
          "sp": "T",
          "tp": "R",
          "tone": "recycle",
          "via": [
            [
              2750,
              150
            ]
          ]
        },
        {
          "from": "P4",
          "to": "E-100",
          "label": "回收甲苯",
          "sp": "L",
          "tp": "R",
          "tone": "recycle"
        },
        {
          "from": "E-100",
          "to": "M2",
          "label": "甲苯循环",
          "sp": "L",
          "tp": "T",
          "tone": "recycle",
          "via": [
            [
              1050,
              150
            ]
          ]
        },
        {
          "from": "F3",
          "to": "V3",
          "label": "含甲醇水相",
          "sp": "B",
          "tp": "T"
        },
        {
          "from": "V3",
          "to": "EC3",
          "label": "",
          "sp": "L",
          "tp": "R"
        },
        {
          "from": "EC3",
          "to": "C3",
          "label": "甲醇回收塔进料",
          "sp": "L",
          "tp": "R",
          "via": [
            [
              1660,
              760
            ],
            [
              1660,
              900
            ]
          ]
        },
        {
          "from": "C3",
          "to": "P3",
          "label": "塔顶甲醇",
          "sp": "T",
          "tp": "R",
          "tone": "recycle",
          "via": [
            [
              1500,
              650
            ]
          ]
        },
        {
          "from": "P3",
          "to": "E4",
          "label": "回收甲醇",
          "sp": "L",
          "tp": "R",
          "tone": "recycle",
          "via": [
            [
              1120,
              650
            ],
            [
              1120,
              800
            ]
          ]
        },
        {
          "from": "E4",
          "to": "M2",
          "label": "甲醇循环",
          "sp": "L",
          "tp": "B",
          "tone": "recycle",
          "via": [
            [
              920,
              800
            ],
            [
              920,
              570
            ],
            [
              1050,
              570
            ]
          ]
        },
        {
          "from": "C3",
          "to": "V4",
          "label": "塔底含水物流",
          "sp": "B",
          "tp": "R",
          "via": [
            [
              1500,
              1190
            ]
          ]
        },
        {
          "from": "V4",
          "to": "E5",
          "label": "",
          "sp": "L",
          "tp": "R"
        },
        {
          "from": "E5",
          "to": "WATER",
          "label": "水出口",
          "sp": "L",
          "tp": "R",
          "tone": "product"
        },
        {
          "from": "C1",
          "to": "V2",
          "label": "乙苯 / 苯乙烯",
          "sp": "B",
          "tp": "T"
        },
        {
          "from": "V2",
          "to": "EC2",
          "label": "",
          "sp": "B",
          "tp": "T"
        },
        {
          "from": "EC2",
          "to": "C2",
          "label": "精制进料",
          "sp": "B",
          "tp": "L",
          "via": [
            [
              2470,
              1250
            ]
          ]
        },
        {
          "from": "C2",
          "to": "P5",
          "label": "塔顶乙苯",
          "sp": "T",
          "tp": "L",
          "via": [
            [
              2750,
              1050
            ]
          ]
        },
        {
          "from": "P5",
          "to": "E6",
          "label": "",
          "sp": "R",
          "tp": "L"
        },
        {
          "from": "E6",
          "to": "EB",
          "label": "乙苯产品",
          "sp": "R",
          "tp": "L",
          "tone": "product"
        },
        {
          "from": "C2",
          "to": "P6",
          "label": "塔底苯乙烯",
          "sp": "B",
          "tp": "L",
          "via": [
            [
              2750,
              1480
            ]
          ]
        },
        {
          "from": "P6",
          "to": "E7",
          "label": "",
          "sp": "R",
          "tp": "L"
        },
        {
          "from": "E7",
          "to": "ST",
          "label": "苯乙烯产品",
          "sp": "R",
          "tp": "L",
          "tone": "product"
        }
      ]
    }
  }
];

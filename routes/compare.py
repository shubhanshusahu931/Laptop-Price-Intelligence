# routes/compare.py — CPU Benchmark Database (deduplicated, unified key: "score")
from flask import Blueprint, jsonify

compare_bp = Blueprint('compare', __name__)

CPU_DB = [
  # ── INTEL i3 ──
  {"id":"i3-11","name":"Intel Core i3 11th Gen","score":{"perf":30,"multi":28,"single":38,"power":80,"gaming":20,"ai":10},"arch":"Tiger Lake","tdp":"15W","cores":"2C/4T","cache":"6MB","nm":"10nm","freq":"4.1 GHz","pv":30000},
  {"id":"i3-12","name":"Intel Core i3 12th Gen","score":{"perf":38,"multi":35,"single":45,"power":78,"gaming":25,"ai":20},"arch":"Alder Lake","tdp":"15W","cores":"6C/8T","cache":"10MB","nm":"Intel 7","freq":"4.4 GHz","pv":35000},
  {"id":"i3-13","name":"Intel Core i3 13th Gen","score":{"perf":42,"multi":38,"single":48,"power":75,"gaming":28,"ai":22},"arch":"Raptor Lake","tdp":"15W","cores":"6C/8T","cache":"10MB","nm":"Intel 7","freq":"4.5 GHz","pv":38000},
  {"id":"i3-14","name":"Intel Core i3 14th Gen","score":{"perf":45,"multi":40,"single":50,"power":72,"gaming":30,"ai":25},"arch":"Raptor Lake R","tdp":"15W","cores":"6C/8T","cache":"10MB","nm":"Intel 7","freq":"4.7 GHz","pv":42000},
  # ── INTEL i5 ──
  {"id":"i5-11","name":"Intel Core i5 11th Gen","score":{"perf":48,"multi":45,"single":52,"power":65,"gaming":45,"ai":28},"arch":"Tiger Lake","tdp":"28W","cores":"4C/8T","cache":"8MB","nm":"10nm","freq":"4.4 GHz","pv":45000},
  {"id":"i5-12","name":"Intel Core i5 12th Gen","score":{"perf":55,"multi":52,"single":60,"power":58,"gaming":56,"ai":40},"arch":"Alder Lake","tdp":"28W","cores":"10C/12T","cache":"18MB","nm":"Intel 7","freq":"4.4 GHz","pv":50000},
  {"id":"i5-13","name":"Intel Core i5 13th Gen","score":{"perf":60,"multi":57,"single":64,"power":55,"gaming":60,"ai":44},"arch":"Raptor Lake","tdp":"28W","cores":"12C/16T","cache":"24MB","nm":"Intel 7","freq":"4.6 GHz","pv":52000},
  {"id":"i5-14","name":"Intel Core i5 14th Gen","score":{"perf":63,"multi":60,"single":66,"power":53,"gaming":62,"ai":46},"arch":"Raptor Lake R","tdp":"28W","cores":"12C/16T","cache":"24MB","nm":"Intel 7","freq":"4.7 GHz","pv":54000},
  # ── INTEL i7 ──
  {"id":"i7-11","name":"Intel Core i7 11th Gen","score":{"perf":65,"multi":62,"single":64,"power":55,"gaming":65,"ai":35},"arch":"Tiger Lake","tdp":"45W","cores":"8C/16T","cache":"24MB","nm":"10nm","freq":"4.8 GHz","pv":65000},
  {"id":"i7-12","name":"Intel Core i7 12th Gen","score":{"perf":70,"multi":68,"single":68,"power":54,"gaming":70,"ai":50},"arch":"Alder Lake","tdp":"45W","cores":"14C/20T","cache":"24MB","nm":"Intel 7","freq":"4.7 GHz","pv":70000},
  {"id":"i7-13","name":"Intel Core i7 13th Gen","score":{"perf":76,"multi":74,"single":72,"power":50,"gaming":75,"ai":55},"arch":"Raptor Lake","tdp":"45W","cores":"16C/24T","cache":"30MB","nm":"Intel 7","freq":"5.0 GHz","pv":75000},
  {"id":"i7-14","name":"Intel Core i7 14th Gen","score":{"perf":79,"multi":77,"single":74,"power":48,"gaming":78,"ai":57},"arch":"Raptor Lake R","tdp":"45W","cores":"16C/24T","cache":"30MB","nm":"Intel 7","freq":"5.2 GHz","pv":78000},
  # ── INTEL i9 ──
  {"id":"i9-11","name":"Intel Core i9 11th Gen","score":{"perf":75,"multi":78,"single":72,"power":35,"gaming":80,"ai":45},"arch":"Tiger Lake","tdp":"45W","cores":"8C/16T","cache":"24MB","nm":"10nm","freq":"5.0 GHz","pv":85000},
  {"id":"i9-12","name":"Intel Core i9 12th Gen","score":{"perf":82,"multi":80,"single":78,"power":42,"gaming":82,"ai":58},"arch":"Alder Lake","tdp":"45W","cores":"14C/20T","cache":"24MB","nm":"Intel 7","freq":"5.0 GHz","pv":95000},
  {"id":"i9-13","name":"Intel Core i9 13th Gen","score":{"perf":86,"multi":85,"single":80,"power":38,"gaming":84,"ai":60},"arch":"Raptor Lake","tdp":"55W","cores":"24C/32T","cache":"36MB","nm":"Intel 7","freq":"5.4 GHz","pv":110000},
  {"id":"i9-14","name":"Intel Core i9 14th Gen","score":{"perf":88,"multi":87,"single":82,"power":36,"gaming":86,"ai":62},"arch":"Raptor Lake R","tdp":"55W","cores":"24C/32T","cache":"36MB","nm":"Intel 7","freq":"5.6 GHz","pv":120000},
  # ── INTEL ULTRA ──
  {"id":"u5-125h","name":"Intel Core Ultra 5 125H","score":{"perf":74,"multi":76,"single":72,"power":75,"gaming":65,"ai":70},"arch":"Meteor Lake","tdp":"28W","cores":"14C/18T","cache":"18MB","nm":"Intel 4","freq":"4.5 GHz","pv":85000},
  {"id":"u5-226v","name":"Intel Core Ultra 5 226V","score":{"perf":78,"multi":72,"single":80,"power":90,"gaming":70,"ai":85},"arch":"Lunar Lake","tdp":"17W","cores":"8C/8T","cache":"8MB","nm":"TSMC 3nm","freq":"4.5 GHz","pv":95000},
  {"id":"c5-120u","name":"Intel Core 5 120U","score":{"perf":62,"multi":58,"single":65,"power":82,"gaming":45,"ai":30},"arch":"Raptor Lake R","tdp":"15W","cores":"10C/12T","cache":"12MB","nm":"Intel 7","freq":"5.0 GHz","pv":60000},
  {"id":"u7-155h","name":"Intel Core Ultra 7 155H","score":{"perf":82,"multi":84,"single":78,"power":70,"gaming":75,"ai":78},"arch":"Meteor Lake","tdp":"28W","cores":"16C/22T","cache":"24MB","nm":"Intel 4","freq":"4.8 GHz","pv":105000},
  {"id":"u7-258v","name":"Intel Core Ultra 7 258V","score":{"perf":84,"multi":80,"single":86,"power":92,"gaming":78,"ai":90},"arch":"Lunar Lake","tdp":"17W","cores":"8C/8T","cache":"12MB","nm":"TSMC 3nm","freq":"4.8 GHz","pv":120000},
  {"id":"c7-150u","name":"Intel Core 7 150U","score":{"perf":68,"multi":65,"single":70,"power":80,"gaming":50,"ai":35},"arch":"Raptor Lake R","tdp":"15W","cores":"10C/12T","cache":"12MB","nm":"Intel 7","freq":"5.4 GHz","pv":75000},
  {"id":"u9-185h","name":"Intel Core Ultra 9 185H","score":{"perf":86,"multi":88,"single":82,"power":65,"gaming":80,"ai":82},"arch":"Meteor Lake","tdp":"45W","cores":"16C/22T","cache":"24MB","nm":"Intel 4","freq":"5.1 GHz","pv":135000},
  {"id":"u9-288v","name":"Intel Core Ultra 9 288V","score":{"perf":88,"multi":85,"single":90,"power":94,"gaming":82,"ai":95},"arch":"Lunar Lake","tdp":"30W","cores":"8C/8T","cache":"12MB","nm":"TSMC 3nm","freq":"5.1 GHz","pv":150000},
  {"id":"c3-100u","name":"Intel Core 3 100U","score":{"perf":45,"multi":42,"single":50,"power":85,"gaming":30,"ai":20},"arch":"Raptor Lake R","tdp":"15W","cores":"6C/8T","cache":"10MB","nm":"Intel 7","freq":"4.7 GHz","pv":45000},
  # ── AMD RYZEN 3 ──
  {"id":"r3-3k","name":"AMD Ryzen 3 3250U","score":{"perf":25,"multi":22,"single":30,"power":85,"gaming":15,"ai":5},"arch":"Zen+","tdp":"15W","cores":"2C/4T","cache":"4MB","nm":"12nm","freq":"3.5 GHz","pv":28000},
  {"id":"r3-5k","name":"AMD Ryzen 3 5300U","score":{"perf":32,"multi":30,"single":38,"power":82,"gaming":22,"ai":12},"arch":"Zen 2","tdp":"15W","cores":"4C/8T","cache":"4MB","nm":"7nm","freq":"3.8 GHz","pv":32000},
  {"id":"r3-7k","name":"AMD Ryzen 3 7320U","score":{"perf":35,"multi":32,"single":40,"power":84,"gaming":20,"ai":18},"arch":"Mendocino","tdp":"15W","cores":"4C/8T","cache":"4MB","nm":"6nm","freq":"4.1 GHz","pv":35000},
  # ── AMD RYZEN 5 ──
  {"id":"r5-4k","name":"AMD Ryzen 5 4500U","score":{"perf":45,"multi":42,"single":48,"power":75,"gaming":38,"ai":20},"arch":"Zen 2","tdp":"15W","cores":"6C/6T","cache":"8MB","nm":"7nm","freq":"4.0 GHz","pv":38000},
  {"id":"r5-5k","name":"AMD Ryzen 5 5500U","score":{"perf":56,"multi":54,"single":58,"power":62,"gaming":55,"ai":38},"arch":"Zen 2/3","tdp":"25W","cores":"6C/12T","cache":"11MB","nm":"7nm","freq":"4.0 GHz","pv":42000},
  {"id":"r5-6k","name":"AMD Ryzen 5 6600H","score":{"perf":62,"multi":60,"single":62,"power":60,"gaming":64,"ai":42},"arch":"Zen 3+","tdp":"45W","cores":"6C/12T","cache":"16MB","nm":"6nm","freq":"4.5 GHz","pv":55000},
  {"id":"r5-7k","name":"AMD Ryzen 5 7640HS","score":{"perf":68,"multi":66,"single":70,"power":65,"gaming":72,"ai":65},"arch":"Zen 4","tdp":"35W","cores":"6C/12T","cache":"16MB","nm":"4nm","freq":"5.0 GHz","pv":68000},
  # ── AMD RYZEN 7 ──
  {"id":"r7-5k","name":"AMD Ryzen 7 5800H","score":{"perf":72,"multi":74,"single":68,"power":50,"gaming":74,"ai":48},"arch":"Zen 3","tdp":"45W","cores":"8C/16T","cache":"16MB","nm":"7nm","freq":"4.4 GHz","pv":72000},
  {"id":"r7-6k","name":"AMD Ryzen 7 6800H","score":{"perf":76,"multi":78,"single":72,"power":55,"gaming":78,"ai":55},"arch":"Zen 3+","tdp":"45W","cores":"8C/16T","cache":"20MB","nm":"6nm","freq":"4.7 GHz","pv":80000},
  {"id":"r7-7k","name":"AMD Ryzen 7 7745HX","score":{"perf":82,"multi":84,"single":76,"power":52,"gaming":82,"ai":65},"arch":"Zen 4","tdp":"55W","cores":"8C/16T","cache":"32MB","nm":"4nm","freq":"5.1 GHz","pv":88000},
  {"id":"r7-8k","name":"AMD Ryzen 7 8845HS","score":{"perf":84,"multi":82,"single":78,"power":60,"gaming":80,"ai":78},"arch":"Zen 4","tdp":"45W","cores":"8C/16T","cache":"24MB","nm":"4nm","freq":"5.1 GHz","pv":90000},
  # ── AMD RYZEN 9 ──
  {"id":"r9-5k","name":"AMD Ryzen 9 5900HX","score":{"perf":80,"multi":82,"single":75,"power":40,"gaming":80,"ai":55},"arch":"Zen 3","tdp":"45W","cores":"8C/16T","cache":"20MB","nm":"7nm","freq":"4.6 GHz","pv":90000},
  {"id":"r9-6k","name":"AMD Ryzen 9 6900HX","score":{"perf":85,"multi":86,"single":78,"power":45,"gaming":84,"ai":60},"arch":"Zen 3+","tdp":"45W","cores":"8C/16T","cache":"20MB","nm":"6nm","freq":"4.9 GHz","pv":100000},
  {"id":"r9-7k","name":"AMD Ryzen 9 7945HX","score":{"perf":94,"multi":98,"single":85,"power":35,"gaming":92,"ai":70},"arch":"Zen 4","tdp":"55W","cores":"16C/32T","cache":"64MB","nm":"4nm","freq":"5.4 GHz","pv":125000},
  {"id":"r9-8k","name":"AMD Ryzen 9 8945HS","score":{"perf":90,"multi":89,"single":82,"power":58,"gaming":88,"ai":85},"arch":"Zen 4","tdp":"45W","cores":"8C/16T","cache":"24MB","nm":"4nm","freq":"5.2 GHz","pv":115000},
  {"id":"r9-9k","name":"AMD Ryzen 9 9950HX","score":{"perf":97,"multi":99,"single":92,"power":42,"gaming":96,"ai":95},"arch":"Zen 5","tdp":"55W","cores":"16C/32T","cache":"80MB","nm":"4nm","freq":"5.7 GHz","pv":150000},
  # ── APPLE M-SERIES ──
  {"id":"m1",    "name":"Apple M1",    "score":{"perf":74,"multi":72,"single":82,"power":95,"gaming":60,"ai":72},"arch":"ARM","tdp":"10W","cores":"8C","cache":"12MB","nm":"5nm","freq":"3.2 GHz","pv":65000},
  {"id":"m1-pro","name":"Apple M1 Pro","score":{"perf":82,"multi":84,"single":82,"power":88,"gaming":72,"ai":75},"arch":"ARM","tdp":"30W","cores":"10C","cache":"24MB","nm":"5nm","freq":"3.2 GHz","pv":120000},
  {"id":"m1-max","name":"Apple M1 Max","score":{"perf":88,"multi":90,"single":82,"power":80,"gaming":82,"ai":78},"arch":"ARM","tdp":"60W","cores":"10C","cache":"48MB","nm":"5nm","freq":"3.2 GHz","pv":180000},
  {"id":"m2",    "name":"Apple M2",    "score":{"perf":80,"multi":79,"single":86,"power":95,"gaming":65,"ai":78},"arch":"ARM","tdp":"10W","cores":"8C","cache":"16MB","nm":"5nm","freq":"3.5 GHz","pv":80000},
  {"id":"m2-pro","name":"Apple M2 Pro","score":{"perf":86,"multi":88,"single":86,"power":85,"gaming":78,"ai":82},"arch":"ARM","tdp":"30W","cores":"12C","cache":"30MB","nm":"5nm","freq":"3.5 GHz","pv":150000},
  {"id":"m2-max","name":"Apple M2 Max","score":{"perf":90,"multi":92,"single":86,"power":78,"gaming":88,"ai":85},"arch":"ARM","tdp":"60W","cores":"12C","cache":"38MB","nm":"5nm","freq":"3.7 GHz","pv":210000},
  {"id":"m3",    "name":"Apple M3",    "score":{"perf":86,"multi":84,"single":90,"power":96,"gaming":70,"ai":82},"arch":"ARM","tdp":"10W","cores":"8C","cache":"16MB","nm":"3nm","freq":"4.0 GHz","pv":105000},
  {"id":"m3-pro","name":"Apple M3 Pro","score":{"perf":91,"multi":90,"single":92,"power":92,"gaming":82,"ai":88},"arch":"ARM","tdp":"25W","cores":"12C","cache":"24MB","nm":"3nm","freq":"4.0 GHz","pv":180000},
  {"id":"m3-max","name":"Apple M3 Max","score":{"perf":96,"multi":98,"single":92,"power":85,"gaming":90,"ai":94},"arch":"ARM","tdp":"60W","cores":"16C","cache":"48MB","nm":"3nm","freq":"4.0 GHz","pv":280000},
  {"id":"m4",    "name":"Apple M4",    "score":{"perf":92,"multi":91,"single":94,"power":97,"gaming":74,"ai":92},"arch":"ARM","tdp":"10W","cores":"10C","cache":"20MB","nm":"3nm","freq":"4.4 GHz","pv":135000},
  {"id":"m4-pro","name":"Apple M4 Pro","score":{"perf":97,"multi":98,"single":96,"power":90,"gaming":92,"ai":96},"arch":"ARM","tdp":"30W","cores":"14C","cache":"32MB","nm":"3nm","freq":"4.5 GHz","pv":220000},
  {"id":"m4-max","name":"Apple M4 Max","score":{"perf":99,"multi":100,"single":98,"power":82,"gaming":98,"ai":98},"arch":"ARM","tdp":"60W","cores":"16C","cache":"48MB","nm":"3nm","freq":"4.5 GHz","pv":320000},
]

@compare_bp.route("/compare/cpus", methods=["GET"])
def list_cpus():
    seen, unique = set(), []
    for c in CPU_DB:
        if c["id"] not in seen:
            seen.add(c["id"])
            unique.append({"id": c["id"], "name": c["name"]})
    return jsonify(unique)

@compare_bp.route("/compare/cpus/<id_a>/<id_b>", methods=["GET"])
def compare_cpus(id_a, id_b):
    a = next((c for c in CPU_DB if c["id"] == id_a), None)
    b = next((c for c in CPU_DB if c["id"] == id_b), None)
    if not a or not b:
        return jsonify({"error": "CPU not found. Use /compare/cpus for valid IDs"}), 404
    score_a = sum(a["score"].values())
    score_b = sum(b["score"].values())
    winner  = a if score_a >= score_b else b
    return jsonify({
        "cpu_a": a, "cpu_b": b,
        "score_a": score_a, "score_b": score_b,
        "winner_id": winner["id"], "winner_name": winner["name"]
    })

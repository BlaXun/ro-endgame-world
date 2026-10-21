import csv,sys
# merge_csv.py monsters.csv < rows (AegisName,BaseExp,JobExp,note): set those monsters' experience; an old
# note's other parts (after its calibration, or all of it if it was not one) are kept
p=sys.argv[1]; rows=list(csv.DictReader(open(p))); cols=list(rows[0].keys())
for name,be,je,note in csv.reader(sys.stdin):
    o=next((r for r in rows if r['AegisName']==name),None)
    if o is None: o=dict.fromkeys(cols,''); o['AegisName']=name; rows.append(o)
    old=o.get('note','')
    rest=old.split('; ',1)[1] if old.startswith('calibrated') and '; ' in old else ('' if old.startswith('calibrated') else old)
    o['BaseExp']=be; o['JobExp']=je; o['note']=note+('; '+rest if rest else '')
with open(p,'w',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=cols,lineterminator='\n'); w.writeheader(); w.writerows(rows)

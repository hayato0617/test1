import pymupdf, numpy as np
S='/tmp/claude-0/-home-user-test1/2f2cabaa-6eae-53d9-81fa-2072ba00a88c/scratchpad'
NEW='/root/.claude/uploads/2f2cabaa-6eae-53d9-81fa-2072ba00a88c/dadf98e3-soukatuzur8.pdf'
OLD=S+'/web/old.pdf'
OUT='/home/user/test1/output/小牧市区画整理総括図_R8.pdf'
A=np.load(S+'/work/A.npy'); ZO=2.3; ZN=7017/842
def T(p):
    x,y=p.x*ZO,p.y*ZO
    q=A@np.array([x,y,1.0]); return pymupdf.Point(q[0]/ZN,q[1]/ZN)
SC=ZO*1.0016/ZN
src=pymupdf.open(NEW); old=pymupdf.open(OLD)
out=src; pg=out[0]; pg.remove_rotation(); print('page',pg.rect,pg.rotation)
FONT='/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'
pg.insert_font(fontname='ipag',fontfile=FONT); F=pymupdf.Font(fontfile=FONT)
BLUE=(0.0,0.35,0.67); ORG=(0.96,0.47,0.13); GRN=(0.27,0.73,0.45); INK=(0.14,0.12,0.13)

# --- 1. 区画整理区域界（旧総括図のベクタを座標変換して転記）
r2=lambda t: tuple(round(v,2) for v in t) if t else None
sh=pg.new_shape(); n=0
for x in old[0].get_drawings():
    c=r2(x.get('color')); w=round(x.get('width') or 0,2)
    if x['type']!='s' or (x['rect'].x0>1400 and x['rect'].y0>1560): continue
    if not ((c==(0.0,0.35,0.67) and w==0.99) or (c==(0.0,0.0,1.0) and w==1.0)): continue
    for it in x['items']:
        k=it[0]
        if k=='l': sh.draw_line(T(it[1]),T(it[2]))
        elif k=='c': sh.draw_bezier(T(it[1]),T(it[2]),T(it[3]),T(it[4]))
        elif k=='re':
            r=it[1]; sh.draw_polyline([T(r.tl),T(r.tr),T(r.br),T(r.bl),T(r.tl)])
        elif k=='qu':
            q=it[1]; sh.draw_polyline([T(q.ul),T(q.ur),T(q.lr),T(q.ll),T(q.ul)])
    sh.finish(color=BLUE,width=0.35,closePath=x.get('closePath',False),lineCap=1,lineJoin=1); n+=1
sh.commit(); print('boundary paths',n)

# --- 2. 番号マーカー（旧図の位置。色：橙=市施行、緑=組合施行）
CITY={3,4,5,6,9,10,12,13,14,15,16,18,21}
M=[(12,561.7,1251.1),(15,896.3,1417.6),(16,982.6,817.3),(14,995.7,707.8),(14,1119.2,740.3),
   (18,1215.5,826.8),(13,1189.2,694.5),(10,1065.1,574.4),(6,692.6,1285.6),(4,830.8,1371.6),
   (9,984.3,1144.3),(5,1103.4,640.5),(8,472.9,1342.1),(2,884.2,1224.3),(7,712.4,985.6),
   (19,558.9,1168.6),(11,1103.9,689.3),(17,1011.4,1315.1),(1,958.3,1727.9),(20,970.7,909.9),(21,1421.2,793.7)]
R=6.8*SC
def label(cx,cy,txt,fs):
    tw=F.text_length(txt,fontsize=fs)
    pg.insert_text((cx-tw/2,cy+fs*0.36),txt,fontname='ipag',fontsize=fs,color=INK)
# 20番の引出線
sh=pg.new_shape(); sh.draw_line(T(pymupdf.Point(967.5,930.5)),T(pymupdf.Point(973.5,922.0))); sh.finish(color=INK,width=0.4); sh.commit()
for num,x0,y0 in M:
    c=T(pymupdf.Point(x0+6.8,y0+6.8))
    pg.draw_circle(c,R,color=INK,fill=ORG if num in CITY else GRN,width=0.12)
    label(c.x,c.y,str(num),2.1 if num<10 else 1.9)
for txt,(x0,y0,x1,y1) in [('3-1',(583.7,1016.9,606.4,1030.5)),('3-2',(847.4,1006.2,870.1,1019.8))]:
    a=T(pymupdf.Point(x0,y0)); b=T(pymupdf.Point(x1,y1)); h=(b.y-a.y)
    pg.draw_rect(pymupdf.Rect(a,b),color=INK,fill=ORG,width=0.12,radius=0.5)
    label((a.x+b.x)/2,(a.y+b.y)/2,txt,2.0)

# --- 3. 表題の差し替え
pg.draw_rect(pymupdf.Rect(34,58,200,78),color=None,fill=(1,1,1),width=0)
x=21.0
for ch in '小牧市区画整理総括図':
    pg.insert_text((x,75.0),ch,fontname='ipag',fontsize=14.6,color=(0.1,0.1,0.1),render_mode=2,border_width=0.04)
    x+=17.6

# --- 4. 土地区画整理事業一覧表（拡大図の位置に配置）
rows=[('1','東原','1.1','S31～S39','S31.11.6','S39.4.8','22.30'),
('2','小牧','10.0','S39～S47','S39.9.25','S44.3.7','32.10'),
('3','中部','88.6','S41～S49','S41.11.9','S50.1.17','23.00'),
('4','桜井','23.5','S42～S49','S42.4.26','S49.11.13','29.70'),
('5','久保一色','23.6','S47～S53','S48.2.28','S54.3.2','25.31'),
('6','市之久田','134.2','S50～S61','S50.6.30','S61.11.21','26.71'),
('7','山北','10.7','S51～S55','S52.3.18','S55.3.31','29.51'),
('8','小木','54.5','S52～H元','S53.2.13','H元.6.30','27.28'),
('9','駅東','54.8','S53～H4','S53.4.18','H5.1.22','30.13'),
('10','久保一色第二','13.4','S56～S62','S56.8.13','S62.11.20','27.67'),
('11','観音堂','1.2','S56～S61','S57.3.29','S61.10.24','29.98'),
('12','川西','19.8','S59～H2','S59.12.26','H3.1.7','17.17'),
('13','小松寺','53.5','H3～R5','H3.10.25','H30.10.26','17.62'),
('14','岩崎山前','62.2','H4～R11','H4.11.11','','21.86'),
('15','小牧南','94.0','H6～R11','H7.3.10','','24.15'),
('16','小牧原北屋敷','17.0','H7～H20','H7.12.1','H20.11.14','24.88'),
('17','小牧大山','1.6','H8～H11','H8.11.20','H11.11.14','31.68'),
('18','文津','37.6','H10～R12','H10.11.30','','24.51'),
('19','小牧堀の内','4.0','H15～H20','H15.9.9','H20.2.29','35.42'),
('20','小牧原樋下','2.0','R1～R6','R1.7.26','R6.2.16','40.04'),
('21','本庄','25.4','R3～R17','R3.10.4','','20.08')]
X0,Y0,X1,Y1=368.0,440.6,526.4,555.0   # 旧「名鉄小牧駅付近拡大図」の枠
pg.draw_rect(pymupdf.Rect(X0-0.6,Y0-0.6,X1+0.6,Y1+0.6),color=None,fill=(1,1,1),width=0)
pg.draw_rect(pymupdf.Rect(X0,Y0,X1,Y1),color=INK,width=0.4)
fs=2.75
def txt(x0,x1,y,s,al='c',f=fs,col=INK):
    tw=F.text_length(s,fontsize=f)
    xx={'c':(x0+x1-tw)/2,'r':x1-0.8-tw,'l':x0+0.8}[al]
    pg.insert_text((xx,y),s,fontname='ipag',fontsize=f,color=col)
title_h=8.0
txt(X0,X1,Y0+5.6,'小牧市土地区画整理事業一覧表',f=4.2)
txt(X0,X1,Y0+5.6,'令和7年3月18日現在',al='r',f=2.6)
cols=[10,25,13,21,21,21,13]; cw=sum(cols); cols[-1]+= (X1-X0)-cw-14; cols.append(14)
xs=[X0]; [xs.append(xs[-1]+c) for c in cols]
hy0=Y0+title_h; hh=7.4; legend_h=6.6
rh=(Y1-legend_h-hy0-hh)/len(rows)
yb=Y1-legend_h
for i in range(len(xs)):
    pg.draw_line((xs[i],hy0),(xs[i],yb),color=INK,width=0.25)
pg.draw_line((X0,hy0),(X1,hy0),color=INK,width=0.3)
pg.draw_line((X0,hy0+hh),(X1,hy0+hh),color=INK,width=0.3)
heads=[('対図','番号'),('地区名',''),('施行面積','ha'),('施行年度',''),('事業計画','決定'),('換地処分',''),('減歩率','%'),('備考','')]
for i,(a,b) in enumerate(heads):
    if b: txt(xs[i],xs[i+1],hy0+3.2,a,f=2.5); txt(xs[i],xs[i+1],hy0+6.4,b,f=2.5)
    else: txt(xs[i],xs[i+1],hy0+4.8,a,f=2.5)
for j,r in enumerate(rows):
    y=hy0+hh+rh*(j+1)
    if j<len(rows)-1: pg.draw_line((X0,y),(X1,y),color=INK,width=0.15)
    base=y-rh/2+fs*0.36
    num=int(r[0]); cx=(xs[0]+xs[1])/2; cy=y-rh/2
    pg.draw_circle((cx,cy),1.75,color=INK,fill=ORG if num in CITY else GRN,width=0.1)
    label(cx,cy,r[0],1.9 if num>=10 else 2.1)
    txt(xs[1],xs[2],base,r[1],f=fs if len(r[1])<=4 else 2.35)
    txt(xs[2],xs[3],base,r[2],al='r'); txt(xs[3],xs[4],base,r[3])
    txt(xs[4],xs[5],base,r[4]); txt(xs[5],xs[6],base,r[5]); txt(xs[6],xs[7],base,r[6],al='r')
    if not r[5]: txt(xs[7],xs[8],base,'施行中',f=2.4)
pg.draw_line((X0,yb),(X1,yb),color=INK,width=0.3)
# 凡例（区画整理関係）
ly=yb+legend_h/2; lx=X0+2
pg.draw_circle((lx+1.8,ly),1.75,color=INK,fill=ORG,width=0.1); txt(lx+4,lx+40,ly+1.0,'市施行土地区画整理箇所',al='l',f=2.6)
lx+=38
pg.draw_circle((lx+1.8,ly),1.75,color=INK,fill=GRN,width=0.1); txt(lx+4,lx+40,ly+1.0,'組合施行土地区画整理箇所',al='l',f=2.6)
lx+=40
pg.draw_rect(pymupdf.Rect(lx,ly-1.5,lx+7,ly+1.5),color=BLUE,width=0.35); txt(lx+8,lx+40,ly+1.0,'土地区画整理区域界',al='l',f=2.6)
txt(X0,X1-1,ly+1.0,'S:昭和 H:平成 R:令和',al='r',f=2.3)
out.set_metadata({'title':'小牧市区画整理総括図','subject':'令和8年3月印刷の小牧市都市計画図を下図とし、土地区画整理事業一覧表（令和7年3月18日現在）を反映'})
out.save(OUT,garbage=3,deflate=True); print(OUT)

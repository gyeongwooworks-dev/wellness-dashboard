import pandas as pd, numpy as np, json, os

ROOT="/sessions/hopeful-elegant-cerf/mnt/ozcoding-dashboard/FitBit Fitness Tracker Data/archive data"
F1=ROOT+"/mturkfitbit_export_3.12.16-4.11.16/Fitabase Data 3.12.16-4.11.16"
F2=ROOT+"/mturkfitbit_export_4.12.16-5.12.16/Fitabase Data 4.12.16-5.12.16"
def rd(b,f): return pd.read_csv(os.path.join(b,f))
out={}

# ---- daily merge ----
da=pd.concat([rd(F1,"dailyActivity_merged.csv"),rd(F2,"dailyActivity_merged.csv")],ignore_index=True)
da["ActivityDate"]=pd.to_datetime(da["ActivityDate"],format="%m/%d/%Y")
da=da.drop_duplicates(subset=["Id","ActivityDate"]).sort_values(["Id","ActivityDate"])
da["ActiveMinutes"]=da["VeryActiveMinutes"]+da["FairlyActiveMinutes"]
users=sorted(da["Id"].unique().tolist())
UL={u:f"U{str(i+1).zfill(2)}" for i,u in enumerate(users)}
out["users"]=[{"id":str(u),"label":UL[u]} for u in users]
GLOBAL_START=da["ActivityDate"].min(); GLOBAL_END=da["ActivityDate"].max()
GLOBAL_DAYS=(GLOBAL_END-GLOBAL_START).days+1

def daily_for(df):
    g=df.groupby("ActivityDate").agg(Calories=("Calories","mean"),TotalSteps=("TotalSteps","mean"),
        ActiveMinutes=("ActiveMinutes","mean"),SedentaryMinutes=("SedentaryMinutes","mean")).reset_index()
    return g
daily={"ALL":None}
g=daily_for(da)
daily["ALL"]={"dates":[d.strftime("%m/%d") for d in g["ActivityDate"]],"calories":g["Calories"].round(0).tolist(),
    "steps":g["TotalSteps"].round(0).tolist(),"active":g["ActiveMinutes"].round(1).tolist()}
for u in users:
    gg=daily_for(da[da.Id==u])
    daily[UL[u]]={"dates":[d.strftime("%m/%d") for d in gg["ActivityDate"]],"calories":gg["Calories"].round(0).tolist(),
        "steps":gg["TotalSteps"].round(0).tolist(),"active":gg["ActiveMinutes"].round(1).tolist()}
out["daily"]=daily

# ---- hourly merge ----
def loadh(b): return rd(b,"hourlyCalories_merged.csv"),rd(b,"hourlyIntensities_merged.csv"),rd(b,"hourlySteps_merged.csv")
hc=pd.concat([loadh(F1)[0],loadh(F2)[0]]); hi=pd.concat([loadh(F1)[1],loadh(F2)[1]]); hs=pd.concat([loadh(F1)[2],loadh(F2)[2]])
for d in (hc,hi,hs):
    d["ActivityHour"]=pd.to_datetime(d["ActivityHour"],format="%m/%d/%Y %I:%M:%S %p"); d["hour"]=d["ActivityHour"].dt.hour; d["Id"]=d["Id"].astype("int64")
stepc=[c for c in hs.columns if c.lower().startswith("step")][-1]
def hourly_for(uid=None):
    c,it,st=hc,hi,hs
    if uid is not None: c=c[c.Id==uid]; it=it[it.Id==uid]; st=st[st.Id==uid]
    cg=c.groupby("hour")["Calories"].mean(); ig=it.groupby("hour")["TotalIntensity"].mean(); sg=st.groupby("hour")[stepc].mean()
    H=range(24)
    return {"cal":[round(float(cg.get(h,0)),1) for h in H],"intensity":[round(float(ig.get(h,0)),2) for h in H],"steps":[round(float(sg.get(h,0)),0) for h in H]}
hourly={"ALL":hourly_for()}
for u in users: hourly[UL[u]]=hourly_for(u)
out["hourly"]=hourly

# ---- sleep (F2) ----
sd=rd(F2,"sleepDay_merged.csv"); sd["SleepDay"]=pd.to_datetime(sd["SleepDay"],format="%m/%d/%Y %I:%M:%S %p").dt.normalize()
sd["efficiency"]=(sd["TotalMinutesAsleep"]/sd["TotalTimeInBed"]*100).round(1); sd["sleepHours"]=(sd["TotalMinutesAsleep"]/60).round(2)
di=da.set_index(["Id","ActivityDate"]); scatter=[]
for _,r in sd.iterrows():
    uid=int(r.Id); nd=r.SleepDay+pd.Timedelta(days=1); key=(uid,nd)
    if key in di.index:
        row=di.loc[key]; row=row.iloc[0] if isinstance(row,pd.DataFrame) else row
        scatter.append({"user":UL.get(uid,str(uid)),"eff":float(r.efficiency),"nextSteps":int(row.TotalSteps)})
out["sleepScatter"]=scatter
ex=np.array([s["eff"] for s in scatter]); ny=np.array([s["nextSteps"] for s in scatter])
out["sleepCorr"]=round(float(np.corrcoef(ex,ny)[0,1]),3); a,b=np.polyfit(ex,ny,1)
out["sleepReg"]={"slope":float(a),"intercept":float(b),"xmin":float(ex.min()),"xmax":float(ex.max())}

# ---- heart rate merge ----
hr=pd.concat([rd(F1,"heartrate_seconds_merged.csv"),rd(F2,"heartrate_seconds_merged.csv")],ignore_index=True)
hr["Time"]=pd.to_datetime(hr["Time"],format="%m/%d/%Y %I:%M:%S %p"); hr["Id"]=hr.Id.astype("int64")
hr=hr.drop_duplicates(subset=["Id","Time"])
hr_users=sorted(hr.Id.unique().tolist())
zone=lambda v:"rest" if v<100 else "fatburn" if v<120 else "cardio" if v<140 else "peak"
hr["zone"]=hr.Value.apply(zone); hrd={}
for u in hr_users:
    s=hr[hr.Id==u].copy(); zc=s.zone.value_counts(normalize=True); s["day"]=s.Time.dt.date
    bd=s.groupby("day").size().idxmax(); dd=s[s.day==bd].copy(); dd["m"]=dd.Time.dt.floor("min")
    pm=dd.groupby("m").Value.mean().reset_index(); step=max(1,len(pm)//240); pm=pm.iloc[::step]
    hrd[UL[u]]={"zones":{z:round(float(zc.get(z,0))*100,1) for z in ["rest","fatburn","cardio","peak"]},
        "restHR":int(s.Value.quantile(.05)),"maxHR":int(s.Value.max()),"avgHR":int(s.Value.mean()),"sessionDay":str(bd),
        "series":{"t":[t.strftime("%H:%M") for t in pm.m],"v":[round(float(x),0) for x in pm.Value]}}
out["hrUsers"]=[UL[u] for u in hr_users]; out["hr"]=hrd

# ---- per-user engagement / consistency / segments ----
sleep_by=sd.groupby("Id").sleepHours.mean(); eff_by=sd.groupby("Id").efficiency.mean(); hravg=hr.groupby("Id").Value.mean()
def act_seg(steps): return "power" if steps>=10000 else "steady" if steps>=5000 else "sedentary"
def eng_seg(c): return "core" if c>=0.8 else "casual" if c>=0.4 else "atrisk"
summary=[]
for u in users:
    d=da[da.Id==u]
    span=(d.ActivityDate.max()-d.ActivityDate.min()).days+1
    recorded=d.ActivityDate.nunique()
    cons=round(recorded/GLOBAL_DAYS,3)  # 기록 지속성 = 기록일수 / 전체 관측창(62일)
    avgSteps=int(d.TotalSteps.mean())
    summary.append({"user":UL[u],"days":int(recorded),"span":int(span),"consistency":round(cons*100,1),
        "avgSteps":avgSteps,"avgCalories":int(d.Calories.mean()),"avgActive":round(float(d.ActiveMinutes.mean()),1),
        "avgSleepH":round(float(sleep_by.get(u)),2) if u in sleep_by.index else None,
        "avgEff":round(float(eff_by.get(u)),1) if u in eff_by.index else None,
        "avgHR":int(hravg.get(u)) if u in hravg.index else None,
        "actSeg":act_seg(avgSteps),"engSeg":eng_seg(cons)})
out["summary"]=summary

# ---- segment aggregates ----
def seg_counts(key,order):
    c={k:0 for k in order}
    for s in summary: c[s[key]]+=1
    return c
out["segments"]={
  "activity":{"order":["power","steady","sedentary"],"counts":seg_counts("actSeg",["power","steady","sedentary"])},
  "engagement":{"order":["core","casual","atrisk"],"counts":seg_counts("engSeg",["core","casual","atrisk"])}
}
# activity segment characteristics (means) for radar/compare
def seg_stat(seg):
    rows=[s for s in summary if s["actSeg"]==seg]
    def m(k):
        vals=[r[k] for r in rows if r[k] is not None]
        return round(float(np.mean(vals)),1) if vals else None
    # peak activity hour = argmax mean intensity across users in seg
    labs=[r["user"] for r in rows]
    inten=np.zeros(24)
    for lb in labs: inten+=np.array(hourly[lb]["intensity"])
    if labs: inten/=len(labs)
    peak=int(inten.argmax())
    return {"n":len(rows),"avgSteps":m("avgSteps"),"avgCalories":m("avgCalories"),"avgActive":m("avgActive"),
            "avgSleepH":m("avgSleepH"),"avgEff":m("avgEff"),"consistency":m("consistency"),"peakHour":peak}
out["segChar"]={s:seg_stat(s) for s in ["power","steady","sedentary"]}

# ---- personas (derived from activity segments + peak hour) ----
def tod(h): return "아침형" if 5<=h<11 else "오후형" if 11<=h<17 else "저녁형" if 17<=h<22 else "야간형"
persona_meta={
 "power":{"base":"파워무버","desc":"활동량이 매우 높은 핵심 사용자","msg":"챌린지·목표 달성 기능, 프리미엄 코칭 소구"},
 "steady":{"base":"스테디워커","desc":"꾸준한 중간 활동량 사용자","msg":"루틴 유지·소셜 비교 기능으로 습관 강화"},
 "sedentary":{"base":"라이트유저","desc":"활동량이 낮은 사용자","msg":"가벼운 목표·리마인더로 활동 시작 유도"}}
personas=[]
for seg in ["power","steady","sedentary"]:
    c=out["segChar"][seg]; meta=persona_meta[seg]
    personas.append({"seg":seg,"name":f"{tod(c['peakHour'])} {meta['base']}","n":c["n"],"desc":meta["desc"],
        "msg":meta["msg"],"peakHour":c["peakHour"],"avgSteps":c["avgSteps"],"avgCalories":c["avgCalories"],
        "avgEff":c["avgEff"],"consistency":c["consistency"]})
out["personas"]=personas

# ---- weekly active users (participation over time) ----
da["week"]=da.ActivityDate.dt.to_period("W").apply(lambda p:p.start_time)
wk=da.groupby("week").Id.nunique().reset_index().sort_values("week")
out["weeklyActive"]={"weeks":[w.strftime("%m/%d") for w in wk.week],"counts":[int(x) for x in wk.Id]}

# ---- consistency distribution buckets ----
buckets=[("0-20",0,20),("20-40",20,40),("40-60",40,60),("60-80",60,80),("80-100",80,100.1)]
cd=[]
for lab,lo,hi in buckets:
    cd.append({"label":lab,"count":sum(1 for s in summary if lo<=s["consistency"]<hi)})
out["consistencyDist"]=cd

# ---- KPIs ----
active_users=sum(1 for s in summary if s["consistency"]>=40)
out["kpis"]={"nUsers":len(users),"nSleepUsers":int(sd.Id.nunique()),"nHrUsers":len(hr_users),
    "dateStart":GLOBAL_START.strftime("%Y-%m-%d"),"dateEnd":GLOBAL_END.strftime("%Y-%m-%d"),"nDays":int(da.ActivityDate.nunique()),
    "avgSteps":int(da.TotalSteps.mean()),"avgCalories":int(da.Calories.mean()),"avgActive":round(float(da.ActiveMinutes.mean()),1),
    "avgSleepH":round(float(sd.sleepHours.mean()),2),"avgEff":round(float(sd.efficiency.mean()),1),
    "avgRestHR":int(hr.groupby("Id").Value.mean().mean()),"activeUsers":active_users,
    "avgConsistency":round(float(np.mean([s["consistency"] for s in summary])),1)}

json.dump(out,open("/sessions/hopeful-elegant-cerf/mnt/outputs/data_wellness.json","w"),ensure_ascii=False,separators=(",",":"))
print("users:",len(users),"| activity seg:",out["segments"]["activity"]["counts"],"| engage seg:",out["segments"]["engagement"]["counts"])
print("personas:",[(p["name"],p["n"]) for p in personas])
print("avgConsistency:",out["kpis"]["avgConsistency"],"| activeUsers(>=40%):",active_users)
print("weeklyActive weeks:",len(out["weeklyActive"]["weeks"]),"| size:",os.path.getsize("/sessions/hopeful-elegant-cerf/mnt/outputs/data_wellness.json"))

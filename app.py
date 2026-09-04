import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Academic Performance Dashboard",page_icon="🎓",layout="wide")
@st.cache_data
def load_data(): return pd.read_csv("data/academic_performance_dataset.csv")
df=load_data()

st.title("🎓 Academic Performance Dashboard")
st.caption("Interactive analysis of student marks, GPA, attendance and academic risk.")

with st.sidebar:
    st.header("🔎 Filters")
    dept=st.multiselect("Department",sorted(df.Department.unique()),default=sorted(df.Department.unique()))
    year=st.multiselect("Year",sorted(df.Year.unique()),default=sorted(df.Year.unique()))
    sem=st.multiselect("Semester",sorted(df.Semester.unique()),default=sorted(df.Semester.unique()))
    subj=st.multiselect("Subject",sorted(df.Subject.unique()),default=sorted(df.Subject.unique()))
    gender=st.multiselect("Gender",sorted(df.Gender.unique()),default=sorted(df.Gender.unique()))

d=df[df.Department.isin(dept)&df.Year.isin(year)&df.Semester.isin(sem)&df.Subject.isin(subj)&df.Gender.isin(gender)]
if d.empty: st.warning("No records match the selected filters."); st.stop()

c=st.columns(6)
c[0].metric("Total Students",d["Student ID"].nunique())
c[1].metric("Average Marks",f'{d["Total Marks"].mean():.1f}')
c[2].metric("Average GPA",f'{d.GPA.mean():.2f}')
c[3].metric("Avg Attendance",f'{d["Attendance Percentage"].mean():.1f}%')
c[4].metric("Pass Percentage",f'{(d["Pass/Fail Status"].eq("Pass").mean()*100):.1f}%')
c[5].metric("Failed Students",int(d["Pass/Fail Status"].eq("Fail").sum()))

a,b=st.columns(2)
with a:
    x=d.groupby("Department",as_index=False)["Total Marks"].mean()
    st.plotly_chart(px.bar(x,x="Department",y="Total Marks",title="Average Marks by Department"),use_container_width=True)
with b:
    x=d.groupby("Subject",as_index=False)["Total Marks"].mean()
    st.plotly_chart(px.bar(x,x="Subject",y="Total Marks",title="Average Marks by Subject"),use_container_width=True)

a,b=st.columns(2)
with a:
    x=d["Grade"].value_counts().reindex(["O","A+","A","B+","B","C","RA"],fill_value=0).reset_index()
    x.columns=["Grade","Students"]
    st.plotly_chart(px.pie(x,names="Grade",values="Students",hole=.4,title="Grade Distribution"),use_container_width=True)
with b:
    x=d.groupby("Semester",as_index=False)["Total Marks"].mean()
    st.plotly_chart(px.line(x,x="Semester",y="Total Marks",markers=True,title="Semester Performance Trend"),use_container_width=True)

st.plotly_chart(px.scatter(d,x="Attendance Percentage",y="GPA",color="Department",hover_data=["Student Name","Subject","Total Marks"],title="Attendance vs GPA"),use_container_width=True)

a,b=st.columns(2)
with a:
    st.subheader("🏆 Top 10 Students")
    x=d.sort_values(["GPA","Total Marks"],ascending=False).head(10)
    st.dataframe(x[["Student ID","Student Name","Department","Total Marks","GPA","Attendance Percentage"]],use_container_width=True,hide_index=True)
with b:
    st.subheader("📉 Bottom 10 Students")
    x=d.sort_values(["GPA","Total Marks"]).head(10)
    st.dataframe(x[["Student ID","Student Name","Department","Total Marks","GPA","Attendance Percentage"]],use_container_width=True,hide_index=True)

st.subheader("⚠️ At-Risk Students")
risk=d[(d.GPA<6)|(d["Attendance Percentage"]<75)|(d["Total Marks"]<50)].copy()
risk["Risk Reason"]=risk.apply(lambda r:", ".join([x for x,ok in [("Low GPA",r.GPA<6),("Low Attendance",r["Attendance Percentage"]<75),("Low Marks",r["Total Marks"]<50)] if ok]),axis=1)
st.dataframe(risk[["Student ID","Student Name","Department","Year","Semester","Subject","Total Marks","GPA","Attendance Percentage","Risk Reason"]],use_container_width=True,hide_index=True)
st.caption("At-risk rule: GPA < 6 OR Attendance < 75% OR Total Marks < 50.")

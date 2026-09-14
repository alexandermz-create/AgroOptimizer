from __future__ import annotations
import pandas as pd
import plotly.express as px
import streamlit as st
from database import add_crop, delete_crop, get_crops, get_dashboard_stats, init_db, update_crop
from optimizer import optimize_production
from rules import climate_factor, evaluate_rules
from sensors import random_sensors, simulate_sensors

st.set_page_config(page_title="AgroOptimizer", page_icon="🌱", layout="wide", initial_sidebar_state="expanded")
init_db()

st.markdown("""
<style>
.stApp{background:radial-gradient(circle at 10% 10%,rgba(121,169,91,.12),transparent 25%),radial-gradient(circle at 90% 90%,rgba(139,107,74,.10),transparent 25%),#f7faf5}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#214c2d,#2f6b3f 55%,#3f7d48)}
section[data-testid="stSidebar"] *{color:white!important}
.hero{padding:1.6rem 1.8rem;border-radius:22px;background:linear-gradient(135deg,#214c2d,#4f8748 60%,#79a95b);color:white;box-shadow:0 10px 30px rgba(33,76,45,.18);margin-bottom:1.2rem}
.hero h1{margin:0;font-size:2.35rem}.hero p{margin:.45rem 0 0;opacity:.92}
.section-card{background:rgba(255,255,255,.88);border:1px solid rgba(47,107,63,.12);border-radius:18px;padding:1rem 1.1rem;box-shadow:0 6px 22px rgba(33,76,45,.07)}
div[data-testid="stMetric"]{background:white;border:1px solid rgba(47,107,63,.10);padding:12px;border-radius:15px;box-shadow:0 5px 18px rgba(33,76,45,.06)}
</style>
""", unsafe_allow_html=True)

def money(value: float)->str: return f"${value:,.2f}"

def sidebar()->str:
    st.sidebar.markdown('<div style="text-align:center;padding:8px 0 18px;"><div style="font-size:3.2rem;">🌱</div><h2 style="margin:0;">AgroOptimizer</h2><p>Optimización agrícola inteligente</p></div>',unsafe_allow_html=True)
    return st.sidebar.radio("Navegación",["🏠 Dashboard","🌾 Optimizar","📡 Sensores","🧠 Reglas","🗂️ Cultivos","📊 Análisis","🌦️ Escenarios","ℹ️ Proyecto"],label_visibility="collapsed")

def dashboard():
    st.markdown('<div class="hero"><h1>🌱 AgroOptimizer</h1><p>Optimiza cultivos, analiza recursos y simula sensores para apoyar la planificación agrícola.</p></div>',unsafe_allow_html=True)
    stats=get_dashboard_stats(); c1,c2,c3,c4=st.columns(4)
    c1.metric("🌾 Cultivos registrados",stats["crop_count"]); c2.metric("💵 Ganancia media/ha",money(stats["avg_profit"])); c3.metric("💧 Agua media/ha",f'{stats["avg_water"]:,.0f} L'); c4.metric("📐 Cultivos activos",stats["active_count"])
    st.markdown("### Módulos del sistema")
    for col,title,text in zip(st.columns(4),["🌾 Cultivos","🧮 Optimización","📡 Sensores","🧠 Reglas"],["Administra costos, rendimiento, agua y trabajo.","Maximiza la ganancia mediante Programación Lineal.","Simula temperatura, luz, presión y proximidad.","Convierte lecturas en alertas y recomendaciones."]):
        with col: st.markdown(f'<div class="section-card"><h3>{title}</h3><p>{text}</p></div>',unsafe_allow_html=True)

def optimizer_page():
    st.markdown("## 🧮 Optimización de producción"); crops=get_crops(True)
    if not crops: st.warning("No hay cultivos activos."); return
    a,b=st.columns(2)
    with a: hectares=st.number_input("📐 Terreno disponible (ha)",.01,10000.,10.,.5); water=st.number_input("💧 Agua disponible (L)",0.,1e9,50000.,1000.)
    with b: budget=st.number_input("💰 Presupuesto ($)",0.,1e12,50000.,5000.); labor=st.number_input("👨‍🌾 Mano de obra (h)",0.,1e8,300.,10.)
    st.markdown("### Límites máximos por cultivo"); limits={}; cols=st.columns(min(3,len(crops)))
    for i,c in enumerate(crops):
        with cols[i%len(cols)]: limits[int(c["id"])]=st.number_input(f'{c["name"]} — máximo ha',0.,max(hectares,float(c["max_ha"])),min(hectares,float(c["max_ha"])),.5,key=f'limit_{c["id"]}')
    if st.button("🌱 Calcular distribución óptima",type="primary",use_container_width=True):
        r=optimize_production(crops,hectares,water,budget,labor,limits)
        if not r["success"]: st.error(r["message"]); return
        st.success(r["message"]); m=st.columns(4); m[0].metric("💵 Ganancia máxima",money(r["profit"])); m[1].metric("📐 Hectáreas",f'{r["land_used"]:.2f} ha'); m[2].metric("💧 Agua usada",f'{r["water_used"]:,.0f} L'); m[3].metric("💰 Costo",money(r["cost_used"]))
        m=st.columns(4); m[0].metric("👨‍🌾 Trabajo",f'{r["labor_used"]:,.1f} h'); m[1].metric("📐 Terreno libre",f'{r["land_left"]:.2f} ha'); m[2].metric("💧 Agua libre",f'{r["water_left"]:,.0f} L'); m[3].metric("💰 Presupuesto libre",money(r["budget_left"]))
        df=pd.DataFrame(r["crops"]); display=df[df.hectares>1e-6].copy(); display.columns=["Cultivo","Hectáreas","Ganancia","Agua (L)","Costo","Trabajo (h)"]; st.dataframe(display.round(2),use_container_width=True,hide_index=True)
        if not display.empty:
            st.plotly_chart(px.pie(display,names="Cultivo",values="Hectáreas",hole=.45,title="Distribución del terreno"),use_container_width=True)
            st.plotly_chart(px.bar(display,x="Cultivo",y="Ganancia",title="Ganancia estimada por cultivo"),use_container_width=True)

def sensors_page():
    st.markdown("## 📡 Simulador de sensores"); st.caption("Simulación por software de sensores de Sistemas Programables.")
    mode=st.radio("Modo",["Manual","Aleatorio"],horizontal=True)
    if mode=="Manual":
        c=st.columns(5); reading=simulate_sensors(c[0].number_input("🌡️ Temperatura °C",-20.,60.,28.,.5),c[1].number_input("🔆 Luz %",0.,100.,80.,1.),c[2].number_input("💧 Presión bar",0.,10.,2.5,.1),c[3].number_input("📡 Proximidad cm",0.,500.,50.,1.),c[4].number_input("💦 Humedad %",0.,100.,60.,1.))
    else:
        if st.button("🎲 Generar lectura"): st.session_state["reading"]=random_sensors()
        reading=st.session_state.get("reading",random_sensors())
    for col,(label,value) in zip(st.columns(5),[("🌡️ Temperatura",f'{reading.temperature:.1f} °C'),("🔆 Óptico",f'{reading.light:.1f} %'),("💧 Presión",f'{reading.pressure:.2f} bar'),("📡 Proximidad",f'{reading.proximity:.1f} cm'),("💦 Humedad",f'{reading.humidity:.1f} %')]): col.metric(label,value)

def rules_page():
    st.markdown("## 🧠 Motor de reglas lógicas"); reading=st.session_state.get("reading",random_sensors())
    for a in evaluate_rules(reading):
        text=f'**{a["level"]}:** {a["message"]} — {a["action"]}'
        if a["level"]=="Alta": st.error(text)
        elif a["level"]=="Media": st.warning(text)
        elif a["level"]=="Baja": st.info(text)
        else: st.success(text)
    st.code("SI temperatura > 35 Y humedad < 40 → alertar estrés hídrico\nSI presión < 1.0 → revisar riego\nSI luz < 30 → revisar iluminación\nSI proximidad < 20 → alertar objeto cercano",language="text")

def crops_page():
    st.markdown("## 🗂️ Base de datos de cultivos"); crops=get_crops(False)
    if crops:
        df=pd.DataFrame(crops); show=df[["id","name","category","price","yield_per_ha","cost","water","labor","light","min_temp","max_temp","max_ha","active"]].copy(); show.columns=["ID","Cultivo","Categoría","Precio","Rendimiento/ha","Costo/ha","Agua/ha","Trabajo/ha","Luz mínima","Temp. mín.","Temp. máx.","Máx. ha","Activo"]; st.dataframe(show.round(2),use_container_width=True,hide_index=True)
    categories=["Grano","Hortaliza","Frutal","Forraje","Otro"]; st.markdown("### ➕ Registrar cultivo")
    with st.form("add_crop"):
        c=st.columns(3); name=c[0].text_input("Nombre"); category=c[1].selectbox("Categoría",categories); price=c[2].number_input("Precio/unidad ($)",0.,1e7,4000.,100.); yield_ha=c[0].number_input("Rendimiento/ha",0.,1e5,5.,.1); cost=c[1].number_input("Costo/ha ($)",0.,1e7,3000.,100.); labor=c[2].number_input("Trabajo/ha (h)",0.,1e5,20.,1.); water=c[0].number_input("Agua/ha (L)",0.,1e7,4000.,100.); light=c[1].number_input("Luz mínima (%)",0.,100.,40.,1.); min_t=c[2].number_input("Temp. mínima °C",-30.,60.,15.,.5); max_t=c[0].number_input("Temp. máxima °C",-30.,60.,35.,.5); max_ha=c[1].number_input("Máximo recomendado (ha)",0.,10000.,10.,.5); active=c[2].checkbox("Activo",True)
        if st.form_submit_button("Guardar cultivo",type="primary"):
            try: add_crop(name,category,price,yield_ha,cost,labor,water,light,min_t,max_t,max_ha,active); st.success("Cultivo guardado."); st.rerun()
            except Exception as e: st.error(f"No se pudo guardar: {e}")
    if crops:
        selected=st.selectbox("Selecciona un cultivo",crops,format_func=lambda x:f'{x["id"]} — {x["name"]}')
        with st.form("edit_crop"):
            c=st.columns(2); n=c[0].text_input("Nombre",selected["name"]); cat=c[1].selectbox("Categoría",categories,index=categories.index(selected["category"]) if selected["category"] in categories else 0); p=c[0].number_input("Precio",0.,1e7,float(selected["price"]),100.); y=c[1].number_input("Rendimiento/ha",0.,1e5,float(selected["yield_per_ha"]),.1); co=c[0].number_input("Costo/ha",0.,1e7,float(selected["cost"]),100.); la=c[1].number_input("Trabajo/ha",0.,1e5,float(selected["labor"]),1.); w=c[0].number_input("Agua/ha",0.,1e7,float(selected["water"]),100.); li=c[1].number_input("Luz mínima",0.,100.,float(selected["light"]),1.); mn=c[0].number_input("Temp. mínima",-30.,60.,float(selected["min_temp"]),.5); mx=c[1].number_input("Temp. máxima",-30.,60.,float(selected["max_temp"]),.5); mh=c[0].number_input("Máximo ha",0.,10000.,float(selected["max_ha"]),.5); ac=c[1].checkbox("Activo",bool(selected["active"]))
            if st.form_submit_button("Guardar cambios",type="primary"):
                try: update_crop(selected["id"],n,cat,p,y,co,la,w,li,mn,mx,mh,ac); st.success("Cambios guardados."); st.rerun()
                except Exception as e: st.error(f"No se pudo actualizar: {e}")
        if st.button("🗑️ Eliminar cultivo seleccionado"): delete_crop(selected["id"]); st.success("Cultivo eliminado."); st.rerun()

def analysis_page():
    st.markdown("## 📊 Análisis"); crops=get_crops(True)
    if not crops: st.info("Registra cultivos activos."); return
    df=pd.DataFrame(crops); df["profit_ha"]=df.price*df.yield_per_ha-df.cost; df["profit_per_liter"]=df.apply(lambda r:r.profit_ha/r.water if r.water else 0,axis=1)
    a,b=st.columns(2)
    with a: st.plotly_chart(px.bar(df.sort_values("profit_ha",ascending=False),x="name",y="profit_ha",title="Ganancia por hectárea"),use_container_width=True)
    with b: st.plotly_chart(px.scatter(df,x="water",y="profit_ha",size="cost",color="category",hover_name="name",title="Ganancia vs. agua"),use_container_width=True)
    table=df[["name","category","price","yield_per_ha","cost","profit_ha","water","labor","profit_per_liter"]].copy(); table.columns=["Cultivo","Categoría","Precio","Rendimiento","Costo/ha","Ganancia/ha","Agua/ha","Trabajo/ha","Ganancia/L"]; st.dataframe(table.round(2),use_container_width=True,hide_index=True)

def scenarios_page():
    st.markdown("## 🌦️ Escenarios agrícolas"); scenario=st.selectbox("Escenario",["Normal","Sequía","Presupuesto limitado","Alta disponibilidad de agua"]); factor={"Normal":1.,"Sequía":.7,"Presupuesto limitado":1.,"Alta disponibilidad de agua":1.5}[scenario]; crops=get_crops(True)
    if not crops: st.info("No hay cultivos activos."); return
    land=st.number_input("Terreno (ha)",.1,10000.,10.,.5); water=st.number_input("Agua base (L)",0.,1e9,50000.,1000.)*factor; budget=st.number_input("Presupuesto ($)",0.,1e12,50000.,5000.); labor=st.number_input("Mano de obra (h)",0.,1e8,300.,10.); budget*=.6 if scenario=="Presupuesto limitado" else 1
    if st.button("Comparar escenario",type="primary"):
        r=optimize_production(crops,land,water,budget,labor,{int(c["id"]):min(land,float(c["max_ha"])) for c in crops}); st.metric("Ganancia estimada",money(r["profit"])) if r["success"] else st.error(r["message"])
    st.write(f"Factor climático por sensores: **{climate_factor(st.session_state.get('reading',random_sensors())):.2f}**")

def about_page():
    st.markdown("## ℹ️ AgroOptimizer — Proyecto académico"); st.markdown('<div class="section-card"><h3>🌱 Sistema inteligente de optimización agrícola</h3><p>Integra Programación Lineal, Programación Lógica y Funcional, bases de datos, visualización y simulación de Sistemas Programables.</p><ul><li><b>Lineal:</b> maximiza ganancia con restricciones.</li><li><b>Lógica:</b> reglas SI/ENTONCES generan alertas.</li><li><b>Funcional:</b> funciones especializadas transforman datos.</li><li><b>Programables:</b> sensores ópticos, temperatura, presión y proximidad simulados.</li></ul></div>',unsafe_allow_html=True); st.code("Python\nStreamlit\nSciPy\nPandas\nPlotly\nSQLite\nGit + GitHub",language="text")

page=sidebar()
{"🏠 Dashboard":dashboard,"🌾 Optimizar":optimizer_page,"📡 Sensores":sensors_page,"🧠 Reglas":rules_page,"🗂️ Cultivos":crops_page,"📊 Análisis":analysis_page,"🌦️ Escenarios":scenarios_page,"ℹ️ Proyecto":about_page}[page]()

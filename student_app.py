import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from io import BytesIO
import plotly.express as px

from student_analyzer import StudentAnalyzer

# Page configuration
st.set_page_config(
    page_title="Student Performance Analyzer",
    page_icon="📚",
    layout="wide",
)

st.title("🧑🏻‍🎓 Student Performance Analyzer")

# Upload file section
uploaded_file = st.file_uploader("📁 Upload your file (.csv or .xlsx)", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        file_name = uploaded_file.name
        file_ext = os.path.splitext(file_name)[1].lower()

        # Read uploaded file
        if file_ext == '.csv':
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Save a temp file
        temp_file = 'uploaded_file' + file_ext
        df.to_csv(temp_file, index=False) if file_ext == '.csv' else df.to_excel(temp_file, index=False)

        # Initialize analyzer
        analyzer = StudentAnalyzer(temp_file)
        st.success("✅ File uploaded successfully!")

        # Display Class Statistics
        st.subheader("📊 Class Statistics")

        stats = analyzer.get_class_stats()
        average_scores = {subject: values['Average'] for subject, values in stats.items()}
        names = list(average_scores.keys())
        values = list(average_scores.values())

        # Create chart
        fig = px.pie(
            names=names,
            values=values,
            title="Students' Favorite Subjects (Based on Average Scores)",
        )
        fig.update_traces(textinfo='label+percent', textfont_size=14)

        # 👉 Layout: Chart and Table side-by-side
        col1, col2 = st.columns([2, 1])
        with col1:
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.markdown("#### 📊 Average Scores Table")
            st.dataframe(pd.DataFrame(stats).T, use_container_width=True)

        # Student selection
        st.subheader("🎯 Analyze Individual Student")
        student_name = df["Name"].tolist()
        selected_student = st.selectbox("Select a student to analyze", student_name)

        if selected_student:
            analysis = analyzer.analyze_student(selected_student)

            st.subheader(f"📄 Report for {selected_student}")

            # 👉 Layout: Student info in columns
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📈 Rank", analysis['Rank'])
            with col2:
                st.metric("📊 Average Score", analysis['Average'])
            with col3:
                st.metric("🎯 Percentage", f"{analysis['Percentage']}%")

            col1, col2,col3 = st.columns(3)
            with col1:
                st.metric("✅ Best Subject", analysis['Best Subject'])
            with col2:
                st.metric("⚠️ Worst Subject", analysis['Worst Subject'])
            with col3:
                if analysis['Grade']=='O':
                    st.success(f"🏅 Grade: {analysis['Grade']}")
                elif analysis['Grade']=='E':
                    st.success(f"🏅 Grade: {analysis['Grade']}")
                else: 
                    st.metric(f"🏅 Grade:", analysis['Grade'])

            # Scores and chart side-by-side
            st.markdown("### 📝 Scores and Performance")
            score_df = pd.DataFrame.from_dict(analysis['Scores'], orient='index', columns=['Score'])

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 📌 Scores")
                st.dataframe(score_df, use_container_width=True)
            with col2:
                st.markdown("### 📉 Performance Chart")
                analyzer.plot_student_performance(selected_student)
                st.image(f"{selected_student}_scores.png")

            # 👉 Recommendations in expander
            with st.expander("💡 Recommendations", expanded=True):
                recs = analyzer.get_recommendations(selected_student)
                for rec in recs:
                    st.write(f"- {rec}")

            # Download report
            st.markdown("### 📤 Download Report")
            if st.button("Generate & Download Report"):
                filename = analyzer.create_report(selected_student)
                with open(filename, 'rb') as f:
                    st.download_button(
                        label="📥 Download Student Report",
                        data=f,
                        file_name=filename,
                        mime='text/plain',
                    )

    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")

else:
    st.info("ℹ️ Please upload a file (.csv or .xlsx) to begin analysis.")

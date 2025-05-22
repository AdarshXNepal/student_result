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

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stats-container {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .student-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #667eea;
        margin: 1.5rem 0;
    }
    .section-header {
        color: #2c3e50;
        border-bottom: 3px solid #667eea;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    .upload-area {
        border: 2px dashed #667eea;
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        background: linear-gradient(135deg, #f8f9ff 0%, #e6f3ff 100%);
        margin: 1rem 0;
    }
    .upload-area h3 {
        margin: 0 0 0.5rem 0;
        color: #2c3e50;
    }
    .upload-area p {
        margin: 0;
        color: #7f8c8d;
    }
    .recommendation-box {
        background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #e17055;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>🧑🏻‍🎓 Student Performance Analyzer</h1>
    <p style="font-size: 1.2rem; margin-top: 1rem; opacity: 0.9;">
        Upload student data and get comprehensive performance insights
    </p>
</div>
""", unsafe_allow_html=True)

# Upload section with enhanced styling
st.markdown("""
<div class="upload-area">
    <h3>📁 Upload Your Data File</h3>
    <p style="font-size: 15px; font-style: italic; margin: 0;">*Supported formats: CSV (.csv) or Excel (.xlsx)*</p>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("", type=['csv', 'xlsx'], help="Upload your student performance data file")

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
        
        # Success message with custom styling
        st.markdown("""
        <div style="background: linear-gradient(90deg, #00b894 0%, #00cec9 100%); 
                    padding: 1rem; border-radius: 10px; color: white; text-align: center; margin: 1rem 0;">
            <h4>✅ File uploaded successfully!</h4>
            <p>Found {num_students} students in your dataset</p>
        </div>
        """.format(num_students=len(df)), unsafe_allow_html=True)

        # Display Class Statistics
        st.markdown("""
        <div class="stats-container">
            <h2 class="section-header">📊 Class Statistics Overview</h2>
        </div>
        """, unsafe_allow_html=True)

        stats = analyzer.get_class_stats()
        average_scores = {subject: values['Average'] for subject, values in stats.items()}
        names = list(average_scores.keys())
        values = list(average_scores.values())

        # Create enhanced chart
        fig = px.pie(
            names=names,
            values=values,
            title="Students' Favorite Subjects (Based on Average Scores)",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_traces(
            textinfo='label+percent', 
            textfont_size=14,
            marker=dict(line=dict(color='#FFFFFF', width=2))
        )
        fig.update_layout(
            title_font_size=18,
            font=dict(size=12),
            showlegend=True,
            height=500
        )

        # Layout: Chart and Table side-by-side
        col1, col2 = st.columns([2, 1])
        with col1:
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.markdown("#### 📊 Average Scores Summary")
            stats_df = pd.DataFrame(stats).T
            st.dataframe(
                stats_df.style.highlight_max(axis=0, color='lightgreen').format(precision=2),
                use_container_width=True
            )

        # Student selection with enhanced design
        st.markdown("""
        <div class="student-card">
            <h2 class="section-header">🎯 Individual Student Analysis</h2>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            student_name = df["Name"].tolist()
            selected_student = st.selectbox(
                "Choose a student to analyze:", 
                student_name,
                help="Select any student from the dropdown to view their detailed performance report"
            )
        with col2:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
                        padding: 1rem; border-radius: 10px; text-align: center; margin-top: 1.5rem;">
                <h4>📈 Total Students</h4>
                <h2>{len(student_name)}</h2>
            </div>
            """, unsafe_allow_html=True)

        if selected_student:
            analysis = analyzer.analyze_student(selected_student)

            st.markdown(f'<h2 class="section-header">📄 Detailed Report for {selected_student}</h2>', unsafe_allow_html=True)

            # Enhanced metrics display
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📈 Class Rank", f"#{analysis['Rank']}", help="Position in class ranking")
            with col2:
                st.metric("📊 Average Score", f"{analysis['Average']:.1f}", help="Overall average across all subjects")
            with col3:
                st.metric("🎯 Percentage", f"{analysis['Percentage']}%", help="Percentage score achieved")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("✅ Best Subject", analysis['Best Subject'], help="Highest scoring subject")
            with col2:
                st.metric("⚠️ Needs Improvement", analysis['Worst Subject'], help="Subject requiring attention")
            with col3:
                if analysis['Grade']=='O':
                    st.success(f"🏅 Grade: {analysis['Grade']} (Outstanding!)")
                elif analysis['Grade']=='E':
                    st.success(f"🏅 Grade: {analysis['Grade']} (Excellent!)")
                else: 
                    st.info(f"🏅 Grade: {analysis['Grade']}")

            # Scores and chart section
            st.markdown("### 📝 Detailed Performance Analysis")
            score_df = pd.DataFrame.from_dict(analysis['Scores'], orient='index', columns=['Score'])

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 📌 Subject-wise Scores")
                # Enhanced dataframe with styling
                styled_df = score_df.style.apply(
                    lambda x: ['background-color: #d4edda' if v >= 80 
                              else 'background-color: #f8d7da' if v < 60 
                              else 'background-color: #fff3cd' for v in x], axis=0
                ).format({'Score': '{:.0f}'})
                st.dataframe(styled_df, use_container_width=True)
                
                # Add performance indicators
                st.markdown("""
                <div style="font-size: 0.9rem; margin-top: 1rem;">
                    <span style="background-color: #d4edda; padding: 0.3rem; border-radius: 5px;">● Excellent (80+)</span>
                    <span style="background-color: #fff3cd; padding: 0.3rem; border-radius: 5px; margin-left: 0.5rem;">● Good (60-79)</span>
                    <span style="background-color: #f8d7da; padding: 0.3rem; border-radius: 5px; margin-left: 0.5rem;">● Needs Work (<60)</span>
                </div>
                """, unsafe_allow_html=True)
                
            with col2:
                st.markdown("#### 📉 Performance Visualization")
                analyzer.plot_student_performance(selected_student)
                st.image(f"{selected_student}_scores.png")

            # Enhanced recommendations section
            with st.expander("💡 Personalized Recommendations", expanded=True):
                recs = analyzer.get_recommendations(selected_student)
                for i, rec in enumerate(recs, 1):
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%); 
                                padding: 0.8rem; margin: 0.5rem 0; 
                                border-radius: 8px; border-left: 4px solid #ff9800;">
                        <strong>{i}.</strong> {rec}
                    </div>
                    """, unsafe_allow_html=True)

            # Enhanced download section
            st.markdown("### 📤 Export Student Report")
            col1, col2 = st.columns([1, 2])
            with col1:
                if st.button("🎯 Generate Report", type="primary", use_container_width=True):
                    filename = analyzer.create_report(selected_student)
                    st.session_state.report_generated = filename
                    st.success("Report generated successfully!")
                    
            with col2:
                if hasattr(st.session_state, 'report_generated'):
                    with open(st.session_state.report_generated, 'rb') as f:
                        st.download_button(
                            label="📥 Download Student Report",
                            data=f,
                            file_name=st.session_state.report_generated,
                            mime='text/plain',
                            type="secondary",
                            use_container_width=True
                        )

    except Exception as e:
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, #ff7675 0%, #fd79a8 100%); 
                    padding: 1.5rem; border-radius: 10px; color: white; text-align: center;">
            <h4>❌ Oops! Something went wrong</h4>
            <p>{str(e)}</p>
            <small>Please check your file format and try again</small>
        </div>
        """, unsafe_allow_html=True)

else:
    # Enhanced info section when no file is uploaded
    st.markdown("""
    <div style="background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%); 
                padding: 2rem; border-radius: 15px; color: white; text-align: center; margin: 2rem 0;">
        <h3>ℹ️ Welcome to Student Performance Analyzer!</h3>
        <p style="font-size: 1.1rem; margin: 1rem 0;">
            Upload your student data file (.csv or .xlsx) to get started with comprehensive performance analysis
        </p>
        <div style="background: rgba(255,255,255,0.2); padding: 1rem; border-radius: 10px; margin-top: 1rem;">
            <h4>🚀 What you'll get:</h4>
            <p>• Class-wide statistics and subject performance</p>
            <p>• Individual student detailed reports</p>
            <p>• Performance visualizations and charts</p>
            <p>• Personalized recommendations</p>
            <p>• Downloadable reports</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
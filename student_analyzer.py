import pandas as pd
import matplotlib.pyplot as plt
import os

class StudentAnalyzer:
    """A simplified class to analyze student performance data."""
    
    def __init__(self, file_path):
        """Initialize with the path to the student data file."""
        self.file_path = file_path
        self.load_data()
        self.subjects = [col for col in self.data.columns if col != 'Name']
        
        self.pass_threshold = 50  # Default passing score
        
    def load_data(self):
        """Load data from CSV or Excel file."""
        file_extension = os.path.splitext(self.file_path)[1].lower()
        
        if file_extension == '.csv':
            self.data = pd.read_csv(self.file_path)
        elif file_extension in ['.xlsx', '.xls']:
            self.data = pd.read_excel(self.file_path)
        else:
            raise ValueError("Unsupported file format. Please use CSV or Excel file.")
            
        print(f"Data loaded: {len(self.data)} students, {len(self.data.columns)-1} subjects")
    
    def get_class_stats(self):
        stats = {}
        for subject in self.data.columns[1:]:
        # Convert values to numeric, coerce errors to NaN, then drop NaNs
            numeric_values = pd.to_numeric(self.data[subject], errors='coerce')
            stats[subject] = {
            'Average': round(numeric_values.mean(), 1),
            'Highest': numeric_values.max(),
            'Lowest': numeric_values.min()
            }
        return stats
    
    def analyze_student(self, student_name):
        """Get basic analysis for a specific student."""
        if student_name not in self.data['Name'].values:
            return f"Student '{student_name}' not found."
        
        student_data = self.data[self.data['Name'] == student_name].iloc[0]
        
        # Get scores for each subject
        scores = {subject: student_data[subject] for subject in self.subjects}
        
        # Find best and worst subjects
        best_subject = max(scores.items(), key=lambda x: x[1])
        worst_subject = min(scores.items(), key=lambda x: x[1])
        
        # Calculate average score
        average_score = sum(scores.values()) / len(scores)
        
        # Calculate student's rank in class
        self.data['Total'] = self.data[self.subjects].sum(axis=1)
        
        # Total marks of that student
        total_score = sum(scores.values())
        percentage = round((total_score / (len(self.subjects) * 100)) * 100, 2)
        
        if percentage > 90:
            Grade='O'
        elif percentage <90 and percentage >80:
            Grade='E'
        elif percentage <80 and percentage >70:
            Grade='A'
        else:
            Grade='F'
        
        #percentage=(self.data['Total']*100/len(self.subjects))
        sorted_data = self.data.sort_values('Total', ascending=False).reset_index(drop=True)
        rank = sorted_data[sorted_data['Name'] == student_name].index[0] + 1
        
        return {
            'Name': student_name,
            'Scores': scores,
            'Best Subject': f"{best_subject[0]} ({best_subject[1]})",
            'Worst Subject': f"{worst_subject[0]} ({worst_subject[1]})",
            'Average': round(average_score, 1),
            'Percentage':percentage,
            'Grade':Grade,
            'Rank': f"{rank} out of {len(self.data)}"
        }
    
    def get_recommendations(self, student_name):
        """Get  recommendations for a student."""
        analysis = self.analyze_student(student_name)
        if isinstance(analysis, str):  # Error message
            return analysis
            
        recommendations = []
        
        # Check for failing subjects
        failing_subjects = []
        for subject, score in analysis['Scores'].items():
            if score < self.pass_threshold:
                failing_subjects.append(subject)
                
        if failing_subjects:
            recommendations.append(f"Focus on improving {', '.join(failing_subjects)}")
        
        # Add general recommendation based on average
        if analysis['Average'] >= 80 or analysis['Percentage']>90:
            recommendations.append(f"Great work! Keep it up! Percentage-{analysis['Percentage']} ")
        elif analysis['Average'] >= 65 or analysis['Percentage']>80:
            recommendations.append(f"Good progress. Try to improve your weaker subjects {analysis['Worst Subject']}. Percentage -{analysis['Percentage']} and average-{analysis['Average']}")
        else:
            recommendations.append(f"Consider getting additional help with {analysis['Worst Subject']}.Percentage -{analysis['Percentage']} and average-{analysis['Average']}")
            
        return recommendations
    
    def plot_student_performance(self, student_name):
        """Create a  bar chart of student performance."""
        if student_name not in self.data['Name'].values:
            print(f"Student '{student_name}' not found.")
            return None
            
        student_data = self.data[self.data['Name'] == student_name].iloc[0]
        
        plt.figure(figsize=(10, 6))
        
        # Create bars with different colors based on scores
        bars = plt.bar(self.subjects, [student_data[subject] for subject in self.subjects])
        
        for bar, subject in zip(bars, self.subjects):
            score = student_data[subject]
            if score >= 80:
                bar.set_color('green')
            elif score >= 65:
                bar.set_color('yellow')
            else:
                bar.set_color('red')
        
        # Add pass threshold line
        plt.axhline(y=self.pass_threshold, color='r', linestyle='--', label=f'Pass Threshold')
        
        plt.title(f"{student_name}'s Performance")
        plt.xlabel('Subjects')
        plt.ylabel('Scores')
        plt.ylim(0, 100)
        plt.legend()
        
        # Save the figure
        plt.savefig(f"{student_name}_scores.png")
        plt.close()
        
        print(f"Chart saved as {student_name}_scores.png")
        
    def create_report(self, student_name):
        """Create a  text report for a student."""
        analysis = self.analyze_student(student_name)
        if isinstance(analysis, str):  # Error message
            return analysis
            
        recommendations = self.get_recommendations(student_name)
        
        report = [
            f"STUDENT REPORT: {student_name}",
            f"==========================",
            f"",
            f"Rank: {analysis['Rank']}",
            f"Average Score: {analysis['Average']}",
            f'Percentage:{analysis['Percentage']}',
            f"Grade:{analysis['Grade']}"
            f"",
            f"SCORES:",
        ]
        
        # Add each subject score
        for subject, score in analysis['Scores'].items():
            status = "PASS" if score >= self.pass_threshold else "FAIL"
            report.append(f"{subject}: {score} ({status})")
        
        report.extend([
            f"",
            f"Best Subject: {analysis['Best Subject']}",
            f"Worst Subject: {analysis['Worst Subject']}",
            f"Percentage:{analysis['Percentage']}",
            f"Grade:{analysis['Grade']}"
            f"",
            f"RECOMMENDATIONS:"
        ])
        
        # Add recommendations
        for i, rec in enumerate(recommendations, 1):
            report.append(f"{i}. {rec}")
            
        # Write report to file
        filename = f"{student_name}_report.txt"
        with open(filename, 'w') as f:
            f.write('\n'.join(report))
            
        print(f"Report saved as {filename}")
        return filename

# Example usage
if __name__ == "__main__":
    # Create sample data
    sample_data = pd.DataFrame({
        'Name': ['Alex', 'Beth', 'Carlos', 'Diana', 'Ethan'],
        'Math': [75, 92, 65, 48, 82],
        'Science': [68, 88, 72, 55, 70],
        'English': [82, 95, 60, 62, 78],
        'History': [70, 85, 55, 59, 80]
    })
    
    # Save sample data
    sample_file = 'students_.csv'
    sample_data.to_csv(sample_file, index=False)
    print(f"Sample data created: {sample_file}")
    
    # Create analyzer and demonstrate
    analyzer = StudentAnalyzer(sample_file)
    
    # Print class stats
    print("\nClass Statistics:")
    class_stats = analyzer.get_class_stats()
    for subject, stats in class_stats.items():
        print(f"{subject}: Average {stats['Average']}, Range {stats['Lowest']}-{stats['Highest']}")
    
    # Analyze student
    student = 'Beth'
    print(f"\nAnalyzing {student}:")
    analysis = analyzer.analyze_student(student)
    if not isinstance(analysis, str):
        print(f"Average: {analysis['Average']}")
        print(f"Rank: {analysis['Rank']}")
        print(f"Best: {analysis['Best Subject']}")
        print(f"Percentage:{analysis['Percentage']}")
        print(f"Grade:{analysis['Grade']}")
        print(f"Worst: {analysis['Worst Subject']}")
    
    # Get recommendations
    print("\nRecommendations:")
    recs = analyzer.get_recommendations(student)
    for rec in recs:
        print(f"- {rec}")
    
    # Create chart and report
    analyzer.plot_student_performance(student)
    report_file = analyzer.create_report(student)
    
    print(f"\nAnalysis complete! Check {report_file} and {student}_scores.png")
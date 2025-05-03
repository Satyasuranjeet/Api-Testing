import streamlit as st
import requests
import time

# Set page configuration with dark theme
st.set_page_config(
    page_title="Student CRUD App",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="🎓"
)

# Apply dark theme with custom CSS - simplified version
st.markdown("""
<style>
    /* Dark theme styles */
    .stApp {
        background-color: #121212;
        color: #f1f1f1;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #f1f1f1;
    }

    /* Custom container styling */
    .student-card {
        background-color: #1e1e1e;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 3px solid #0e76a8; 
    }
    
    /* Button styling */
    .stButton button {
        border-radius: 5px;
        color:black;
    }
    
    /* Add student form */
    .add-form {
        background-color: #1e1e1e;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        margin-bottom: 20px;
        padding: 10px;
        background-color: #0e76a8;
        border-radius: 8px;
        color: white;
    }
    
    /* Input field styling */
    .stTextInput input, .stNumberInput input {
        background-color: #2d2d2d;
        color: white;
        border: 1px solid #444;
        border-radius: 5px;
    }
    
    /* Divider */
    hr {
        margin-top: 20px;
        margin-bottom: 20px;
        border: 0;
        border-top: 1px solid #333;
    }
    
    /* Stats cards */
    .stat-card {
        background-color: #1e1e1e;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        border-bottom: 3px solid #0e76a8;
    }
    
    .stat-number {
        font-size: 24px;
        font-weight: bold;
        color: #0e76a8;
    }
    
    .stat-label {
        font-size: 14px;
        color: #aaa;
    }
</style>
""", unsafe_allow_html=True)

API_BASE_URL = "http://localhost:8000/students/"

# Initialize session state
if "students" not in st.session_state:
    st.session_state.students = []
if "loading" not in st.session_state:
    st.session_state.loading = False
if "show_form" not in st.session_state:
    st.session_state.show_form = False
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False
if "current_student" not in st.session_state:
    st.session_state.current_student = {}

# API functions
def fetch_students():
    st.session_state.loading = True
    try:
        response = requests.get(API_BASE_URL)
        if response.status_code == 200:
            students = response.json()
            st.session_state.students = students
            return students
        else:
            st.error("Failed to fetch students")
            return []
    except Exception as e:
        st.error(f"API Error: {e}")
        return []
    finally:
        st.session_state.loading = False

def create_student(name, age, university):
    st.session_state.loading = True
    payload = {"name": name, "age": age, "university": university}
    try:
        response = requests.post(API_BASE_URL, json=payload)
        if response.status_code == 200:
            st.success("Student added successfully!")
            fetch_students()  # Refresh the list
        else:
            st.error(f"Failed to add student: {response.text}")
        return response
    except Exception as e:
        st.error(f"API Error: {e}")
    finally:
        st.session_state.loading = False

def update_student(student_id, name, age, university):
    st.session_state.loading = True
    payload = {"name": name, "age": age, "university": university}
    try:
        response = requests.put(f"{API_BASE_URL}{student_id}", json=payload)
        if response.status_code == 200:
            st.success("Student updated successfully!")
            fetch_students()  # Refresh the list
            st.session_state.edit_mode = False  # Exit edit mode
        else:
            st.error(f"Update failed: {response.text}")
        return response
    except Exception as e:
        st.error(f"API Error: {e}")
    finally:
        st.session_state.loading = False

def delete_student(student_id):
    st.session_state.loading = True
    try:
        response = requests.delete(f"{API_BASE_URL}{student_id}")
        if response.status_code == 200:
            st.success("Student deleted successfully!")
            fetch_students()  # Refresh the list
        else:
            st.error("Deletion failed.")
        return response
    except Exception as e:
        st.error(f"API Error: {e}")
    finally:
        st.session_state.loading = False

# Set to edit mode
def set_edit_mode(student):
    st.session_state.edit_mode = True
    st.session_state.current_student = student

# Main App UI
def app_header():
    st.markdown("<div class='main-header'><h1>🎓 Student-University Record Manager</h1></div>", unsafe_allow_html=True)

    # Display stats in cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">{}</div>
            <div class="stat-label">Total Students</div>
        </div>
        """.format(len(st.session_state.students)), unsafe_allow_html=True)
    
    with col2:
        # Calculate average age if there are students
        avg_age = 0
        if st.session_state.students:
            avg_age = sum(student['age'] for student in st.session_state.students) / len(st.session_state.students)
            avg_age = round(avg_age, 1)
        
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">{}</div>
            <div class="stat-label">Average Age</div>
        </div>
        """.format(avg_age), unsafe_allow_html=True)
    
    with col3:
        # Count unique universities
        universities = set()
        if st.session_state.students:
            for student in st.session_state.students:
                universities.add(student['university'])
        
        st.markdown("""
        <div class="stat-card">
            <div class="stat-number">{}</div>
            <div class="stat-label">Universities</div>
        </div>
        """.format(len(universities)), unsafe_allow_html=True)

def show_add_student_form():
    with st.expander("➕ Add New Student", expanded=st.session_state.show_form):
        st.markdown("<div class='add-form'>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input("Name", key="add_name")
        with col2:
            age = st.number_input("Age", min_value=1, max_value=100, step=1, key="add_age")
        with col3:
            university = st.text_input("University", key="add_university")
         
        if st.button("Add Student", key="btn_add"):
            if name and university and age:
                create_student(name, int(age), university)
                # Clear the fields
                st.session_state.add_name = ""
                st.session_state.add_age = 18  # Default age
                st.session_state.add_university = ""
                st.session_state.show_form = False  # Close the form after submission
            else:
                st.warning("⚠️ Please fill in all fields.")
        
        st.markdown("</div>", unsafe_allow_html=True)

def show_edit_student_form():
    if st.session_state.edit_mode and st.session_state.current_student:
        student = st.session_state.current_student
        st.markdown("<div class='add-form'>", unsafe_allow_html=True)
        st.subheader(f"Edit Student: {student['name']}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input("Name", value=student['name'], key="edit_name")
        with col2:
            age = st.number_input("Age", value=student['age'], min_value=1, max_value=100, step=1, key="edit_age")
        with col3:
            university = st.text_input("University", value=student['university'], key="edit_university")
         
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Update Student", key="btn_update"):
                if name and university and age:
                    update_student(student['id'], name, int(age), university)
                else:
                    st.warning("⚠️ Please fill in all fields.")
        with col2:
            if st.button("Cancel", key="btn_cancel"):
                st.session_state.edit_mode = False
        
        st.markdown("</div>", unsafe_allow_html=True)

def show_students_list():
    st.subheader("📋 All Students")
    
    if not st.session_state.students:
        st.info("No students found. Add some to begin!")
        return
    
    # Group students by university for better organization
    universities = {}
    for student in st.session_state.students:
        uni = student['university']
        if uni not in universities:
            universities[uni] = []
        universities[uni].append(student)
    
    # Display students grouped by university with collapsible sections
    for uni, students in universities.items():
        with st.expander(f"🏫 {uni} ({len(students)} students)", expanded=True):
            for student in students:
                with st.container():
                    st.markdown(f"""
                    <div class="student-card">
                        <h3>{student['name']}</h3>
                        <p>Age: {student['age']} years</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button("✏️ Edit", key=f"edit_{student['id']}"):
                            set_edit_mode(student)
                    with col2:
                        if st.button("🗑️ Delete", key=f"del_{student['id']}"):
                            delete_student(student['id'])

def main():
    app_header()
    
    # Show loading indicator
    if st.session_state.loading:
        st.info("Processing request...")
    
    # Show edit form if in edit mode
    if st.session_state.edit_mode:
        show_edit_student_form()
    else:
        show_add_student_form()
    
    # Show students list
    show_students_list()
    
    # Footer
    st.markdown("---")
    st.markdown("<div style='text-align: center; color: #666;'>© 2023 Student-University Record Manager</div>", unsafe_allow_html=True)

# Fetch students on app load
if not st.session_state.students:
    st.session_state.students = fetch_students()

# Run the main app
if __name__ == "__main__":
    main()
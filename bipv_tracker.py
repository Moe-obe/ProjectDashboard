import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import json
import os

# Set wide page layout
st.set_page_config(layout="wide")

# Custom CSS (unchanged)
# ... [keep the same custom CSS styles] ...

# Project data storage
PROJECTS_FILE = "projects.json"

def load_projects():
    if os.path.exists(PROJECTS_FILE):
        with open(PROJECTS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_projects(projects):
    with open(PROJECTS_FILE, 'w') as f:
        json.dump(projects, f)

# Initialize session state
if 'projects' not in st.session_state:
    st.session_state.projects = load_projects()

if 'current_project' not in st.session_state:
    st.session_state.current_project = None

# Project management functions
def create_project(name):
    if name not in st.session_state.projects:
        st.session_state.projects[name] = {
            'tasks': [],
            'stages': {
                'Planning': '#FF6B6B',
                'Development': '#4ECDC4',
                'Testing': '#45B7D1',
                'Deployment': '#96CEB4'
            }
        }
        save_projects(st.session_state.projects)
        st.session_state.current_project = name
    else:
        st.error("Project name already exists!")

def delete_project(name):
    if name in st.session_state.projects:
        del st.session_state.projects[name]
        save_projects(st.session_state.projects)
        if st.session_state.current_project == name:
            st.session_state.current_project = None

# Dashboard layout
st.title("Applied Research Dashboard 🗓️")

# Project management sidebar
with st.sidebar:
    st.markdown("### Project Management")
    new_project_name = st.text_input("New Project Name")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Create Project"):
            if new_project_name:
                create_project(new_project_name)
            else:
                st.error("Please enter a project name")
    
    project_names = list(st.session_state.projects.keys())
    selected_project = st.selectbox(
        "Load Project",
        [""] + project_names,
        index=0
    )
    
    if selected_project:
        st.session_state.current_project = selected_project
    
    if st.session_state.current_project and st.button("Delete Current Project"):
        delete_project(st.session_state.current_project)
        st.rerun()

# Main functionality only if project is selected
if st.session_state.current_project:
    current_project = st.session_state.projects[st.session_state.current_project]

    # Function to update project data
    def update_project():
        st.session_state.projects[st.session_state.current_project] = current_project
        save_projects(st.session_state.projects)

    # Modified add_task function
    def add_task(name, stage, start_date, end_date):
        current_project['tasks'].append({
            'Task': name,
            'Start': start_date.isoformat(),
            'Finish': end_date.isoformat(),
            'Stage': stage,
            'Color': current_project['stages'][stage]
        })
        update_project()

    # Modified add_stage function
    def add_stage(new_stage, new_color):
        current_project['stages'][new_stage] = new_color
        update_project()

    # Main columns
    col1, col2 = st.columns([1.2, 3.5])

    # Left Column (Management Inputs)
    with col1:
        st.header(f"Project: {st.session_state.current_project}")
        st.subheader("Add New Task")
        with st.form("task_form"):
            task_name = st.text_input("Task Name")
            stage = st.selectbox("Stage", list(current_project['stages'].keys()))
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
            submitted = st.form_submit_button("Add Task")
            
            if submitted:
                if end_date > start_date:
                    add_task(task_name, stage, start_date, end_date)
                else:
                    st.error("End date must be after start date")

        st.subheader("Manage Stages")
        with st.form("stage_form"):
            new_stage = st.text_input("New Stage Name")
            new_color = st.color_picker("Stage Color")
            stage_submitted = st.form_submit_button("Add Stage")
            
            if stage_submitted:
                add_stage(new_stage, new_color)

    # Right Column (Gantt Chart and Task List)
    with col2:
        st.header("Project Timeline")
        
        if current_project['tasks']:
            # Convert date strings back to dates
            df = pd.DataFrame(current_project['tasks'])
            df['Start'] = pd.to_datetime(df['Start'])
            df['Finish'] = pd.to_datetime(df['Finish'])
            
            fig = px.timeline(
                df,
                x_start="Start",
                x_end="Finish",
                y="Task",
                color="Stage",
                color_discrete_map=current_project['stages'],
                title="Project Gantt Chart"
            )
            fig.update_yaxes(autorange="reversed")
            fig.update_layout(
                height=600,
                xaxis_title="Timeline",
                yaxis_title="Tasks",
                margin=dict(l=0, r=0, b=0, t=40)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No tasks added yet. Add tasks using the left panel.")

        # Task list section (modified to use current_project)
        # ... [keep the same task list code but replace st.session_state.tasks with current_project['tasks']] ...

else:
    st.info("Please create or load a project from the sidebar")

# How to run instructions (unchanged)
# ... [keep the same sidebar instructions] ...
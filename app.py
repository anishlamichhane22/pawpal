import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Your daily pet care planner")

# --- Owner & Pet Info ---
st.subheader("Owner & Pet Info")
col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
    available_minutes = st.number_input("Time available today (minutes)", min_value=10, max_value=480, value=120, step=10)
with col2:
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])

st.divider()

# --- Task Entry ---
st.subheader("Tasks")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

col_add, col_clear = st.columns([1, 1])
with col_add:
    if st.button("Add task", use_container_width=True):
        st.session_state.tasks.append(
            {"title": task_title, "duration_minutes": int(duration), "priority": priority}
        )
with col_clear:
    if st.button("Clear all tasks", use_container_width=True):
        st.session_state.tasks = []

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# --- Schedule Generation ---
st.subheader("Generate Schedule")

if st.button("Generate schedule", type="primary", use_container_width=True):
    if not st.session_state.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        owner = Owner(owner_name, available_minutes=int(available_minutes))
        pet = Pet(pet_name, species)
        scheduler = Scheduler(owner, pet)

        for t in st.session_state.tasks:
            scheduler.add_task(Task(t["title"], t["duration_minutes"], t["priority"]))

        scheduled, skipped = scheduler.generate_plan()

        st.success(f"Schedule for **{pet_name}** (owner: {owner_name}) — {int(available_minutes)} min available")

        if scheduled:
            st.markdown("### Planned Tasks")
            for s in scheduled:
                with st.container(border=True):
                    cols = st.columns([2, 1, 1, 1])
                    cols[0].markdown(f"**{s.task.title}**")
                    cols[1].markdown(f"🕐 {s.start_time_str}")
                    cols[2].markdown(f"⏱ {s.task.duration_minutes} min")
                    cols[3].markdown(f"Priority: `{s.task.priority}`")
                    st.caption(f"Why: {s.reason}")

        if skipped:
            st.markdown("### Skipped Tasks")
            for task, reason in skipped:
                st.warning(f"**{task.title}** — {reason}")

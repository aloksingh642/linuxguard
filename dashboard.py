import streamlit as st
import requests
import os




API_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000") 


st.set_page_config(
    page_title="LinuxGuard",
    page_icon="🛡️",
    layout="wide"
)


st.title("🛡️ LinuxGuard")
st.subheader("Intelligent Linux System Health & Storage Manager")

st.divider()


# -----------------------------
# System Health
# -----------------------------

st.subheader("💻 System Health")

try:
    response = requests.get(
        f"{API_URL}/system",
        timeout=5
    )

    if response.status_code == 200:
        system = response.json()

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Disk Usage",
            f"{system['disk_usage_percent']}%"
        )

        col2.metric(
            "System Status",
            system["status"]
        )

        col3.metric(
            "Used Storage",
            f"{system['used'] / (1024**3):.2f} GB"
        )

        col4.metric(
            "Free Storage",
            f"{system['free'] / (1024**3):.2f} GB"
        )

    else:
        st.error("LinuxGuard API returned an error.")

except requests.exceptions.RequestException:
    st.error("LinuxGuard API is not available.")


st.divider()


st.header("Anomaly Detection")

try:
    response = requests.get(
        f"{API_URL}/anomalies",
        timeout=30
    )

    if response.status_code == 200:

        anomaly_data = response.json()

        total_scans = anomaly_data["total_scans"]
        results = anomaly_data["results"]

        anomalies = [
            result
            for result in results
            if result["anomaly"]
        ]

        col1, col2 = st.columns(2)

        col1.metric("Scans analyzed", total_scans)
        col2.metric("Anomalies detected", len(anomalies))



        if not results:
            st.info(
                "No scan history available yet. "
                "Run a storage scan to populate anomaly detection."
            )
        else:
            st.subheader("Storage usage trend")

            import pandas as pd
            import altair as alt

            chart_data = pd.DataFrame({
                "Scan": [result["scan_id"] for result in results],
                "Usage (%)": [
                    result["usage_percent"]
                    for result in results
                ],
                "Anomaly": [
                    result["anomaly"]
                    for result in results
                ]
            })

            line = alt.Chart(chart_data).mark_line().encode(
                x="Scan",
                y="Usage (%)"
            )

            points = alt.Chart(
                chart_data[chart_data["Anomaly"]]
            ).mark_point(size=100).encode(
                x="Scan",
                y="Usage (%)",
                tooltip=["Scan", "Usage (%)"]
            )

            st.altair_chart(
                line + points,
                use_container_width=True
            )

            st.subheader("Storage growth rate")

            growth_data = {
                "Scan": [
                    result["scan_id"]
                    for result in results
                ],
                "Growth rate (bytes/sec)": [
                    result["growth_rate"]
                    for result in results
                ]
            }

            st.line_chart(
                growth_data,
                x="Scan",
                y="Growth rate (bytes/sec)"
            )


        if anomalies:

            st.subheader("Detected anomalies")

            for anomaly in anomalies:

                st.warning(
                    f"Scan #{anomaly['scan_id']} | "
                    f"Disk usage: {anomaly['usage_percent']}%"
                )

                st.write(
                    f"Storage change: "
                    f"{anomaly['change_from_previous'] / (1024**2):.2f} MB"
                )

                st.write(
                    f"Growth rate: "
                    f"{anomaly['growth_rate']:.2f} bytes/sec"
                )

                st.write(
                    f"Reason: {anomaly['reason']}"
                )
                st.write(
                    f"Anomaly score: "
                    f"{anomaly['anomaly_score']:.4f}"
                )

                st.write(
                    f"Timestamp: {anomaly['timestamp']}"
                )

        else:
            st.success("No anomalies detected.")

    else:
        st.error("Could not retrieve anomaly data.")

except requests.RequestException as error:
    st.error(f"Anomaly service unavailable: {error}")
# -----------------------------
# Storage Scan
# -----------------------------

st.subheader("🔍 Storage Scan")

if st.button("Run Storage Scan"):

    try:
        scan_response = requests.post(
            f"{API_URL}/scan",
            timeout=10
        )

        if scan_response.status_code == 200:

            scan = scan_response.json()

            st.success(
                f"Scan completed successfully! "
                f"Scan ID: {scan['scan_id']}"
            )

            col1, col2 = st.columns(2)

            col1.metric(
                "Disk Usage",
                f"{scan['disk_usage_percent']}%"
            )

            col2.metric(
                "Status",
                scan["status"]
            )

        else:
            st.error("Storage scan failed.")

    except requests.exceptions.RequestException:
        st.error("LinuxGuard API is not available.")


st.divider()


# -----------------------------
# Scan History
# -----------------------------

st.subheader("📋 Scan History")

try:

    history_response = requests.get(
        f"{API_URL}/scans",
        timeout=5
    )

    if history_response.status_code == 200:

        scans = history_response.json()

        if scans:

            history_data = []

            for scan in reversed(scans[-10:]):

                history_data.append({
                    "Scan ID": scan["id"],
                    "Disk Usage": f"{scan['usage_percent']}%",
                    "Used Storage": f"{scan['used'] / (1024**3):.2f} GB",
                    "Free Storage": f"{scan['free'] / (1024**3):.2f} GB",
                    "Timestamp": scan["timestamp"]
                })

            st.table(history_data)

        else:

            st.info("No scan history available.")

    else:

        st.error("Could not load scan history.")

except requests.exceptions.RequestException:

    st.error("LinuxGuard API is not available.")

st.divider()

st.subheader("💾 Storage Analysis")

if st.button("📊 Analyze Storage"):

    try:
        analysis_response = requests.get(
            f"{API_URL}/storage-analysis",
            timeout=60
        )

        if analysis_response.status_code == 200:

            analysis = analysis_response.json()

            st.success("Storage analysis completed.")

            st.write(
                f"**Analyzed Path:** {analysis['path']}"
            )

            st.write("### 🗂️ Largest Files")

            largest_files = analysis["largest_files"]

            if largest_files:

                largest_file_data = []

                for file_path, size in largest_files:
                    largest_file_data.append({
                        "File": str(file_path),
                        "Size": f"{size / (1024**2):.2f} MB"
                    })

                st.dataframe(
                    largest_file_data,
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.info("No large files found.")



            st.write("### 📁 File Categories")

            categories = analysis["file_categories"]

            category_sizes = {
                category: data["size"] / (1024**3)
                for category, data in categories.items()
            }

            st.bar_chart(category_sizes)

            st.write("### 📄 File Types")

            file_types = analysis["file_types"]

            file_type_data = []

            for extension, data in file_types.items():
                file_type_data.append({
                    "File Type": extension,
                    "Count": data["count"],
                    "Size": f"{data['size'] / (1024**3):.2f} GB"
                })

            st.dataframe(
                file_type_data,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.error("Storage analysis failed.")

    except requests.exceptions.RequestException:
        st.error("LinuxGuard API is not available.")
        
st.divider()

st.write("Dashboard is running successfully.")

st.divider()

# -----------------------------
# Cleanup Candidates
# -----------------------------

# -----------------------------
# Cleanup Candidates
# -----------------------------

st.subheader("🧹 Cleanup Candidates")

if st.button("🔍 Find Cleanup Candidates"):

    try:
        cleanup_response = requests.get(
            f"{API_URL}/cleanup-candidates",
            params={
                "limit": 50,
                "offset": 0
            },
            timeout=120
        )

        if cleanup_response.status_code == 200:

            cleanup = cleanup_response.json()

            st.session_state["cleanup_candidates"] = cleanup["candidates"]

            st.session_state["cleanup_total"] = cleanup["total_candidates"]

            st.session_state["cleanup_size"] = cleanup["total_size_bytes"]

        else:
            st.error("Could not find cleanup candidates.")

    except requests.exceptions.RequestException:
        st.error("LinuxGuard API is not available.")


# Show candidates if they have already been discovered

if st.session_state.get("cleanup_candidates"):

    candidates = st.session_state["cleanup_candidates"]

    st.success(
        f"Found {st.session_state['cleanup_total']:,} cleanup candidates."
    )

    st.metric(
        "Potential Cleanup Size",
        f"{st.session_state['cleanup_size'] / (1024**3):.2f} GB"
    )

    st.write("### 🗑️ Candidate Files")

    cleanup_data = [
        {"File": file_path}
        for file_path in candidates
    ]

    st.dataframe(
        cleanup_data,
        use_container_width=True,
        hide_index=True
    )

    st.write("### Select a file to clean")

    st.selectbox(
        "Cleanup candidate",
        candidates,
        key="selected_cleanup_file"
    )

else:

    st.info("Click **Find Cleanup Candidates** to scan for files.")

# -----------------------------
# Safe Cleanup
# -----------------------------

st.subheader("🗑️ Safe Cleanup")

cleanup_file = st.text_input(
    "Selected file",
    value=st.session_state.get("selected_cleanup_file", "")
)

confirm_delete = st.checkbox(
    "I understand that this file will be permanently deleted."
)

if st.button("🗑️ Delete File"):

    if not cleanup_file:
        st.warning("Please enter a file path.")

    elif not confirm_delete:
        st.warning("Please confirm the deletion first.")

    elif cleanup_file not in st.session_state.get("cleanup_candidates", []):
        st.error(
            "This file is not in the current cleanup candidate list."
        )

    else:

        try:
            delete_response = requests.post(
                f"{API_URL}/cleanup",
                json={
                    "file_path": cleanup_file,
                    "confirmed": True
                },
                timeout=10
            )

            if delete_response.status_code == 200:

                result = delete_response.json()

                st.success(
                    f"Successfully deleted: {result['file']}"
                )

                st.session_state.pop("selected_cleanup_file", None)

                st.rerun()

            else:

                error = delete_response.json()

                st.error(
                    f"Cleanup failed: {error.get('detail', 'Unknown error')}"
                )

        except requests.exceptions.RequestException:
            st.error("LinuxGuard API is not available.")

            st.divider()

# -----------------------------
# Cleanup History
# -----------------------------

st.subheader("📜 Cleanup History")

try:

    history_response = requests.get(
        f"{API_URL}/cleanup-history",
        timeout=5
    )

    if history_response.status_code == 200:

        cleanup_history = history_response.json()

        if cleanup_history:

            history_data = []

            for action in reversed(cleanup_history[-20:]):
                history_data.append({
                    "File": action["file_path"],
                    "Action": action["action"],
                    "Status": action["status"],
                    "Time": action["timestamp"]
                })

            st.dataframe(
                history_data,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info("No cleanup history available.")

    else:
        st.error("Could not load cleanup history.")

except requests.exceptions.RequestException:
    st.error("LinuxGuard API is not available.")
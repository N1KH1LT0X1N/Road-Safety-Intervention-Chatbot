"""Road Safety Intervention Chatbot - Streamlit Web App."""
import streamlit as st
from utils.api_client import APIClient
import os
from dotenv import load_dotenv

load_dotenv()

# Page config
st.set_page_config(
    page_title="Road Safety Intervention AI",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        background-color: #f9f9f9;
    }
    .confidence-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-weight: bold;
        font-size: 0.9rem;
    }
    .high-confidence {
        background-color: #d4edda;
        color: #155724;
    }
    .medium-confidence {
        background-color: #fff3cd;
        color: #856404;
    }
    .low-confidence {
        background-color: #f8d7da;
        color: #721c24;
    }
</style>
""",
    unsafe_allow_html=True,
)


def get_confidence_badge(confidence: float) -> str:
    """Get confidence badge HTML."""
    percentage = f"{confidence * 100:.0f}%"

    if confidence >= 0.8:
        badge_class = "high-confidence"
        stars = "⭐⭐⭐⭐⭐"
    elif confidence >= 0.6:
        badge_class = "medium-confidence"
        stars = "⭐⭐⭐⭐"
    else:
        badge_class = "low-confidence"
        stars = "⭐⭐⭐"

    return f'<span class="confidence-badge {badge_class}">{stars} {percentage}</span>'


def display_result(result, idx):
    """Display a single result."""
    with st.container():
        st.markdown(f"### {idx}. {result['title']}")

        # Confidence badge
        st.markdown(get_confidence_badge(result["confidence"]), unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"**Category:** {result['category']}")
            st.markdown(f"**Problem:** {result['problem']}")

        with col2:
            st.markdown(f"**IRC Reference:** {result['irc_reference']['code']}")
            st.markdown(f"**Clause:** {result['irc_reference']['clause']}")

        with col3:
            st.markdown(f"**Cost Estimate:** {result['cost_estimate']}")
            st.markdown(f"**Installation Time:** {result.get('installation_time', 'N/A')}")

        # Expandable sections
        with st.expander("📋 Detailed Specifications"):
            specs = result["specifications"]
            if specs.get("dimensions"):
                st.markdown(f"**Dimensions:** {specs['dimensions']}")
            if specs.get("colors"):
                st.markdown(f"**Colors:** {', '.join(specs['colors'])}")
            if specs.get("placement"):
                st.markdown(f"**Placement:** {specs['placement']}")

        with st.expander("📖 Explanation"):
            st.markdown(result["explanation"])

        with st.expander("🔧 Maintenance"):
            st.markdown(result.get("maintenance", "Standard maintenance required"))

        with st.expander("📚 Full IRC Details"):
            st.markdown(f"**IRC Code:** {result['irc_reference']['code']}")
            st.markdown(f"**Clause:** {result['irc_reference']['clause']}")
            st.markdown(f"\n{result['irc_reference']['excerpt']}")

        st.markdown("---")


def main():
    """Main app."""
    # Header
    st.markdown('<div class="main-header">🚦 Road Safety Intervention AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Powered by Google Gemini</div>', unsafe_allow_html=True)

    # Initialize API client
    api_client = APIClient()

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")

        # API Configuration
        with st.expander("🔑 API Configuration", expanded=False):
            api_url = st.text_input("API URL", value=os.getenv("API_URL", "http://localhost:8000"))
            api_key = st.text_input("API Key", value=os.getenv("API_KEY", ""), type="password")

            if st.button("Test Connection"):
                try:
                    client = APIClient(base_url=api_url, api_key=api_key)
                    health = client.health_check()
                    if health["status"] == "healthy":
                        st.success("✅ Connection successful!")
                    else:
                        st.warning(f"⚠️ API status: {health['status']}")
                except Exception as e:
                    st.error(f"❌ Connection failed: {e}")

        # Filters
        st.header("🔍 Filters")

        # Get filter options
        try:
            categories = api_client.get_categories()
            problems = api_client.get_problems()
        except:
            categories = ["Road Sign", "Road Marking", "Traffic Calming Measures"]
            problems = ["Damaged", "Faded", "Missing"]

        selected_categories = st.multiselect("Category", options=categories, default=[])

        selected_problems = st.multiselect("Problem Type", options=problems, default=[])

        # Speed range
        use_speed_filter = st.checkbox("Filter by Speed Range")
        speed_min = None
        speed_max = None

        if use_speed_filter:
            speed_min = st.number_input("Min Speed (km/h)", min_value=0, max_value=200, value=0)
            speed_max = st.number_input("Max Speed (km/h)", min_value=0, max_value=200, value=100)

        # Strategy
        strategy = st.selectbox(
            "Search Strategy",
            options=["auto", "hybrid", "rag", "structured"],
            help="Auto: Automatically select best strategy\nHybrid: Combine RAG and structured search\nRAG: Semantic vector search\nStructured: Exact match queries",
        )

        # Max results
        max_results = st.slider("Max Results", min_value=1, max_value=10, value=5)

        # Database stats
        with st.expander("📊 Database Statistics"):
            try:
                stats = api_client.get_stats()
                st.metric("Total Interventions", stats["total_interventions"])

                st.write("**Categories:**")
                for cat, count in stats["categories"].items():
                    st.write(f"- {cat}: {count}")

            except Exception as e:
                st.error(f"Could not load stats: {e}")

    # Main content
    st.header("🔍 Search for Road Safety Interventions")

    # Quick examples
    examples = [
        "Faded STOP sign on 65 kmph highway",
        "Missing road markings at pedestrian crossing",
        "Damaged speed breaker on urban road",
        "Obstruction blocking road sign visibility",
    ]

    example_choice = st.selectbox("Quick Examples (optional):", [""] + examples)

    # Search box
    query = st.text_area(
        "Describe the road safety issue:", value=example_choice if example_choice else "", height=100, help="Describe the road safety problem in natural language"
    )

    # Search button
    if st.button("🔍 Search", type="primary", use_container_width=True):
        if not query:
            st.warning("⚠️ Please enter a query")
        else:
            with st.spinner("Searching for interventions..."):
                try:
                    # Make API call
                    response = api_client.search(
                        query=query,
                        category=selected_categories if selected_categories else None,
                        problem=selected_problems if selected_problems else None,
                        speed_min=speed_min,
                        speed_max=speed_max,
                        strategy=strategy,
                        max_results=max_results,
                    )

                    # Display results
                    st.success(
                        f"✅ Found {response['metadata']['total_results']} results in {response['metadata']['query_time_ms']}ms"
                    )

                    # Metadata
                    with st.expander("ℹ️ Search Metadata"):
                        st.json(response["metadata"])

                    # Results
                    if response["results"]:
                        st.header("📊 Results")

                        for idx, result in enumerate(response["results"], 1):
                            display_result(result, idx)

                        # AI Synthesis
                        if response.get("synthesis"):
                            st.header("💬 AI Analysis")
                            st.markdown(response["synthesis"])

                    else:
                        st.info("No interventions found. Try adjusting your query or filters.")

                except Exception as e:
                    st.error(f"❌ Error: {e}")
                    st.exception(e)

    # Footer
    st.markdown("---")
    st.markdown(
        """
    <div style="text-align: center; color: #666;">
        <p>Road Safety Intervention AI | Powered by Google Gemini | Version 1.0.0</p>
    </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

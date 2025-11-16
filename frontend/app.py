"""Road Safety Intervention Chatbot - Streamlit Web App."""
import streamlit as st
from utils.api_client import APIClient, APIError, NetworkError, ValidationError
import os
import json
import time
from datetime import datetime
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
    .recommended-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9rem;
        display: inline-block;
        margin-bottom: 1rem;
    }
    .explanation-section {
        background-color: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
    }
    .irc-badge {
        background-color: #e3f2fd;
        color: #1976d2;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        margin: 0.25rem;
        display: inline-block;
    }
    .error-message {
        background-color: #fff3cd;
        border: 1px solid #ffc107;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .empty-state {
        text-align: center;
        padding: 3rem;
        color: #666;
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


def display_explanation(result, is_top_recommendation=False):
    """Display comprehensive explanation component."""
    st.markdown('<div class="explanation-section">', unsafe_allow_html=True)
    
    if is_top_recommendation:
        st.markdown('<div class="recommended-badge">⭐ TOP RECOMMENDATION</div>', unsafe_allow_html=True)
    
    st.markdown("### 💡 Why This Intervention?")
    
    # Show explanation prominently
    if result.get("explanation"):
        st.markdown(result["explanation"])
    else:
        st.markdown("This intervention matches your road safety issue based on the IRC standards database.")
    
    # Note: IRC references are now shown primarily in display_result function
    # This section is kept for backward compatibility but IRC is shown first in main display
    
    st.markdown('</div>', unsafe_allow_html=True)


def display_result(result, idx, is_top_recommendation=False):
    """Display a single result with enhanced layout for evaluation criteria."""
    with st.container():
        # Recommended Intervention Section
        st.markdown(f"## {idx}. {result['title']}")
        
        if is_top_recommendation:
            st.markdown('<div class="recommended-badge">🏆 BEST MATCH</div>', unsafe_allow_html=True)
        
        # Confidence badge
        st.markdown(get_confidence_badge(result["confidence"]), unsafe_allow_html=True)
        
        # IRC Standard References - PRIMARY/PROMINENT DISPLAY
        irc_ref = result.get("irc_reference", {})
        if irc_ref.get("code"):
            st.markdown("---")
            st.markdown("### 📚 IRC Standard Reference (Primary Source)")
            # Large prominent badge
            irc_code = irc_ref.get("code", "N/A")
            irc_clause = irc_ref.get("clause", "N/A")
            st.markdown(
                f'<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; margin: 15px 0;">'
                f'<h3 style="color: white; margin: 0;">📖 {irc_code}</h3>'
                f'<p style="color: white; margin: 5px 0 0 0; font-size: 1.1em;">Clause {irc_clause}</p>'
                f'</div>',
                unsafe_allow_html=True
            )
            
            # Show IRC excerpt prominently (not in expander)
            if irc_ref.get("excerpt"):
                st.markdown("#### 📄 IRC Standard Excerpt:")
                st.info(irc_ref["excerpt"])
            
            st.markdown("---")
        
        # Explanation Section (prominent)
        display_explanation(result, is_top_recommendation=is_top_recommendation)
        
        # Details in columns
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("#### 📋 Basic Information")
            st.markdown(f"**Category:** {result['category']}")
            st.markdown(f"**Problem:** {result['problem']}")
            st.markdown(f"**Type:** {result.get('type', 'N/A')}")

        with col2:
            st.markdown("#### 📊 Specifications")
            specs = result.get("specifications", {})
            if specs.get("dimensions"):
                st.markdown(f"**Dimensions:** {specs['dimensions']}")
            if specs.get("colors"):
                st.markdown(f"**Colors:** {', '.join(specs['colors']) if isinstance(specs['colors'], list) else specs['colors']}")
            if specs.get("placement"):
                st.markdown(f"**Placement:** {specs['placement']}")

        with col3:
            st.markdown("#### 💰 Cost & Time")
            st.markdown(f"**Cost Estimate:** {result['cost_estimate']}")
            st.markdown(f"**Installation Time:** {result.get('installation_time', 'N/A')}")
            if result.get("maintenance"):
                st.markdown(f"**Maintenance:** {result['maintenance'][:50]}...")

        # Expandable detailed sections
        with st.expander("📋 Full Specifications"):
            specs = result.get("specifications", {})
            if specs.get("dimensions"):
                st.markdown(f"**Dimensions:** {specs['dimensions']}")
            if specs.get("colors"):
                st.markdown(f"**Colors:** {', '.join(specs['colors']) if isinstance(specs['colors'], list) else specs['colors']}")
            if specs.get("placement"):
                st.markdown(f"**Placement:** {specs['placement']}")
            if specs.get("shape"):
                st.markdown(f"**Shape:** {specs['shape']}")
            if specs.get("materials"):
                st.markdown(f"**Materials:** {specs['materials']}")

        with st.expander("🔧 Maintenance Details"):
            st.markdown(result.get("maintenance", "Standard maintenance required"))

        # IRC reference is already shown prominently at the top, so we don't need this expander
        # Keeping it for additional details if needed
        with st.expander("📚 Additional IRC Details"):
            irc_ref = result.get("irc_reference", {})
            st.markdown(f"**Full IRC Code:** {irc_ref.get('code', 'N/A')}")
            st.markdown(f"**Clause Number:** {irc_ref.get('clause', 'N/A')}")
            st.info("💡 IRC Standard Reference is displayed prominently at the top of this result.")

        st.markdown("---")


def main():
    """Main app."""
    # Header
    st.markdown('<div class="main-header">🚦 Road Safety Intervention AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Powered by Google Gemini</div>', unsafe_allow_html=True)

    # Initialize session state for API config
    if "api_url" not in st.session_state:
        st.session_state.api_url = os.getenv("API_URL", "http://localhost:8000")
    if "api_key" not in st.session_state:
        st.session_state.api_key = os.getenv("API_KEY", "")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")

        # API Configuration
        with st.expander("🔑 API Configuration", expanded=False):
            api_url = st.text_input("API URL", value=st.session_state.api_url)
            api_key = st.text_input("API Key", value=st.session_state.api_key, type="password")

            if st.button("Test Connection"):
                try:
                    client = APIClient(base_url=api_url, api_key=api_key)
                    health = client.health_check()
                    if health["status"] == "healthy":
                        st.success("✅ Connection successful!")
                        # Save to session state
                        st.session_state.api_url = api_url
                        st.session_state.api_key = api_key
                    else:
                        st.warning(f"⚠️ API status: {health['status']}")
                except Exception as e:
                    st.error(f"❌ Connection failed: {e}")

        # Filters
        st.header("🔍 Filters")

        # Initialize API client with session state values (but don't call API during init)
        api_client = APIClient(base_url=st.session_state.api_url, api_key=st.session_state.api_key)

        # Always use defaults immediately - NO API calls during initialization to avoid blocking deployment
        if "categories" not in st.session_state:
            st.session_state.categories = ["Road Sign", "Road Marking", "Traffic Calming Measures"]
        if "problems" not in st.session_state:
            st.session_state.problems = ["Damaged", "Faded", "Missing"]
        
        # Use cached/default values (no blocking API calls)
        categories = st.session_state.categories
        problems = st.session_state.problems
        
        # Optional: Add a button to refresh filters from API (non-blocking, user-initiated)
        if st.session_state.api_url and "localhost" not in st.session_state.api_url:
            if st.button("🔄 Refresh Filters from API", help="Fetch latest categories and problems"):
                try:
                    with st.spinner("Fetching filters..."):
                        filter_client = APIClient(
                            base_url=st.session_state.api_url, 
                            api_key=st.session_state.api_key,
                            timeout=3
                        )
                        new_categories = filter_client.get_categories()
                        new_problems = filter_client.get_problems()
                        st.session_state.categories = new_categories
                        st.session_state.problems = new_problems
                    st.success("✅ Filters updated!")
                    st.rerun()
                except Exception as e:
                    st.warning(f"⚠️ Could not refresh: {str(e)}. Using default filters.")

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

        # Database stats - lazy loaded only when expander is opened
        with st.expander("📊 Database Statistics"):
            # Only fetch stats when user opens the expander (lazy loading)
            if st.button("📊 Load Statistics", key="load_stats"):
                try:
                    with st.spinner("Loading statistics..."):
                        stats = api_client.get_stats()
                        st.metric("Total Interventions", stats["total_interventions"])

                        st.write("**Categories:**")
                        for cat, count in stats["categories"].items():
                            st.write(f"- {cat}: {count}")
                except Exception as e:
                    st.error(f"Could not load stats: {e}")
            else:
                st.info("Click 'Load Statistics' to fetch database statistics from the API.")

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
            # Initialize session state for retry
            if "last_query" not in st.session_state:
                st.session_state.last_query = None
            if "retry_count" not in st.session_state:
                st.session_state.retry_count = 0
            
            # Show loading state
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                status_text.text("🔍 Searching interventions database...")
                progress_bar.progress(20)
                
                # Make API call
                start_time = time.time()
                response = api_client.search(
                    query=query,
                    category=selected_categories if selected_categories else None,
                    problem=selected_problems if selected_problems else None,
                    speed_min=speed_min,
                    speed_max=speed_max,
                    strategy=strategy,
                    max_results=max_results,
                )
                
                progress_bar.progress(100)
                elapsed_time = time.time() - start_time
                
                # Clear loading indicators
                progress_bar.empty()
                status_text.empty()
                
                # Store query for retry
                st.session_state.last_query = {
                    "query": query,
                    "category": selected_categories,
                    "problem": selected_problems,
                    "speed_min": speed_min,
                    "speed_max": speed_max,
                    "strategy": strategy,
                    "max_results": max_results,
                }
                st.session_state.retry_count = 0

                # Display results
                st.success(
                    f"✅ Found {response['metadata']['total_results']} recommended intervention(s) in {response['metadata']['query_time_ms']}ms"
                )

                # Results
                if response["results"]:
                    st.header("📊 Recommended Road Safety Intervention(s)")
                    
                    # Show top recommendation prominently
                    if len(response["results"]) > 0:
                        display_result(response["results"][0], 1, is_top_recommendation=True)
                    
                    # Show other recommendations
                    if len(response["results"]) > 1:
                        st.subheader("Additional Intervention Options")
                        for idx, result in enumerate(response["results"][1:], 2):
                            display_result(result, idx, is_top_recommendation=False)
                    
                    # Export functionality
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("📥 Download Results (JSON)"):
                            json_str = json.dumps(response, indent=2)
                            st.download_button(
                                label="Download",
                                data=json_str,
                                file_name=f"interventions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json"
                            )
                    with col2:
                        if st.button("📋 Copy to Clipboard"):
                            st.code(json.dumps(response, indent=2), language="json")
                            st.success("Results copied! (Use Ctrl+C)")
                    
                    # AI Synthesis
                    if response.get("synthesis"):
                        st.header("💬 AI Analysis & Recommendations")
                        st.markdown(response["synthesis"])

                else:
                    # Empty state
                    st.markdown('<div class="empty-state">', unsafe_allow_html=True)
                    st.info("📭 No interventions found matching your query.")
                    st.markdown("### Suggestions:")
                    st.markdown("- Try rephrasing your query")
                    st.markdown("- Remove some filters")
                    st.markdown("- Use more general terms")
                    st.markdown("### Example queries:")
                    for example in examples[:3]:
                        if st.button(f"Try: {example}", key=f"example_{example}"):
                            st.session_state.query_text = example
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

                # Metadata (collapsible)
                with st.expander("ℹ️ Search Metadata"):
                    st.json(response["metadata"])

            except NetworkError as e:
                progress_bar.empty()
                status_text.empty()
                st.error("🌐 Network Error: Unable to connect to the API server.")
                st.markdown(f"**Details:** {str(e)}")
                st.markdown("**Suggestions:**")
                st.markdown("- Check your internet connection")
                st.markdown("- Verify the API URL is correct")
                if st.button("🔄 Retry", key="retry_network"):
                    st.rerun()
                    
            except APIError as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"🔌 API Error: {e.message}")
                if e.status_code == 401:
                    st.warning("⚠️ Invalid API key. Please check your API configuration.")
                elif e.status_code == 429:
                    st.warning("⚠️ Rate limit exceeded. Please wait a moment and try again.")
                elif e.status_code >= 500:
                    st.warning("⚠️ Server error. The API server is experiencing issues.")
                    if st.button("🔄 Retry", key="retry_api"):
                        st.rerun()
                else:
                    st.markdown(f"**Status Code:** {e.status_code}")
                    if st.button("🔄 Retry", key="retry_api_error"):
                        st.rerun()
                        
            except ValidationError as e:
                progress_bar.empty()
                status_text.empty()
                st.error("❌ Validation Error: Invalid input provided.")
                st.markdown(f"**Details:** {str(e)}")
                st.markdown("**Please check:**")
                st.markdown("- Query length (minimum 3 characters)")
                st.markdown("- Filter values are valid")
                
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error("❌ An unexpected error occurred.")
                st.markdown(f"**Error:** {str(e)}")
                st.markdown("**Error Type:** " + type(e).__name__)
                
                # Show retry option
                if st.session_state.retry_count < 3:
                    if st.button("🔄 Retry", key="retry_general"):
                        st.session_state.retry_count += 1
                        st.rerun()
                else:
                    st.warning("Maximum retry attempts reached. Please check your query and try again.")
                    
                # Show technical details in expander
                with st.expander("🔍 Technical Details"):
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

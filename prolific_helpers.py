"""
Helper functions for Prolific API interactions and study management.
"""

import json
import uuid
import requests
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from io import StringIO
import pandas as pd


def get_researcher_id(headers: dict) -> str:
    """
    Fetch the Prolific researcher ID.

    Args:
        headers: Dictionary containing API authorization headers

    Returns:
        str: The researcher ID
    """
    res = requests.get("https://api.prolific.com/api/v1/users/me/", headers=headers)
    res.raise_for_status()
    return res.json()["id"]


def create_survey(headers: dict, researcher_id: str, survey_config: dict) -> str:
    """
    Create a Prolific survey with the specified configuration.

    Args:
        headers: Dictionary containing API authorization headers
        researcher_id: The Prolific researcher ID
        survey_config: Dictionary containing survey configuration with keys:
            - title: Survey title
            - question_text: The question to ask
            - answers: List of answer options

    Returns:
        str: The survey ID
    """
    # Generate UUIDs
    section_id = str(uuid.uuid4())
    question_id = str(uuid.uuid4())
    answer_ids = [str(uuid.uuid4()) for _ in survey_config["answers"]]

    # Build answers list
    answers = [
        {"id": answer_id, "value": answer_text}
        for answer_id, answer_text in zip(answer_ids, survey_config["answers"])
    ]

    # Build question structure
    question = {
        "id": question_id,
        "title": survey_config["question_text"],
        "type": "single",
        "answers": answers,
    }

    # Build the payload
    survey_data = {
        "researcher_id": researcher_id,
        "title": survey_config["title"],
        "sections": [
            {
                "id": section_id,
                "title": survey_config["question_text"],
                "questions": [question],
            }
        ],
        "questions": [question],
    }

    response = requests.post(
        "https://api.prolific.com/api/v1/surveys/",
        headers=headers,
        data=json.dumps(survey_data)
    )
    response.raise_for_status()

    return response.json()["_id"]


def create_study(
    headers: dict,
    survey_id: str,
    study_config: dict,
    project_id: str,
    study_type: str = "survey"
) -> str:
    """
    Create a draft Prolific study.

    Args:
        headers: Dictionary containing API authorization headers
        survey_id: The survey ID to link to this study
        study_config: Dictionary containing study configuration with keys:
            - name: Study name
            - internal_name_prefix: Prefix for internal name
            - description: Study description
            - reward: Reward amount in dollars
            - participants: Number of participants
            - estimated_time: Estimated time in minutes
            - max_time: Maximum time in minutes
            - device_compatibility: List of compatible devices
            - privacy_notice: Privacy notice text
        project_id: The Prolific project ID
        study_type: Type of study - "survey" (default) or "external"

    Returns:
        str: The study ID
    """
    # Generate completion code with timestamp
    completion_code = f"AI_DAILYLIFE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Build the study payload
    # Note: Prolific API automatically determines study type from the URL
    # The study_type parameter is kept for API compatibility but may not be sent
    study_data = {
        "name": study_config["name"],
        "internal_name": f"{study_config.get('internal_name_prefix', study_config['name'])} {datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "description": study_config["description"],
        "external_study_url": f"https://prolific.com/surveys/{survey_id}",
        "completion_codes": [
            {
                "code": completion_code,
                "code_type": "COMPLETED",
                "actions": [{"action": "AUTOMATICALLY_APPROVE"}],
            }
        ],
        "estimated_completion_time": study_config["estimated_time"],
        "max_time": study_config["max_time"],
        "reward": int(study_config["reward"] * 100),  # convert to cents
        "total_available_places": study_config["participants"],
        "device_compatibility": study_config["device_compatibility"],
        "peripheral_requirements": [],
        "privacy_notice": study_config["privacy_notice"],
        "project": project_id
    }

    # Create draft study
    study_response = requests.post(
        "https://api.prolific.com/api/v1/studies/",
        headers=headers,
        data=json.dumps(study_data)
    )
    if not study_response.ok:
        error_msg = study_response.text
        try:
            error_json = study_response.json()
            error_msg = json.dumps(error_json, indent=2)
        except:
            pass
        raise requests.exceptions.HTTPError(
            f"{study_response.status_code} Client Error: {study_response.reason}\n"
            f"Response: {error_msg}\n"
            f"Payload: {json.dumps(study_data, indent=2)}"
        )
    study_response.raise_for_status()

    return study_response.json().get("id")


def create_external_study(
    headers: dict,
    external_study_url: str,
    study_config: dict,
    project_id: str,
    completion_code: str = None,
    eligibility_filters: dict = None,
    study_type: str = "external"
) -> str:
    """
    Create a draft Prolific study using an external study link.

    Args:
        headers: Dictionary containing API authorization headers
        external_study_url: The external URL where the study is hosted (e.g., Qualtrics, SurveyMonkey, etc.)
        study_config: Dictionary containing study configuration with keys:
            - name: Study name
            - internal_name_prefix: Prefix for internal name (optional)
            - description: Study description
            - reward: Reward amount in dollars
            - participants: Number of participants
            - estimated_time: Estimated time in minutes
            - max_time: Maximum time in minutes
            - device_compatibility: List of compatible devices (e.g., ["desktop", "tablet", "mobile"])
            - privacy_notice: Privacy notice text
        project_id: The Prolific project ID
        completion_code: Optional completion code. If not provided, will be auto-generated.
        eligibility_filters: Optional dictionary containing eligibility filters. See Prolific API docs for structure.
        study_type: Type of study - "external" (default) or "survey"

    Returns:
        str: The study ID

    Example:
        >>> study_config = {
        ...     "name": "External Survey Study",
        ...     "description": "A study hosted on an external platform",
        ...     "reward": 2.50,
        ...     "participants": 50,
        ...     "estimated_time": 10,
        ...     "max_time": 15,
        ...     "device_compatibility": ["desktop", "tablet"],
        ...     "privacy_notice": "Your data will be kept confidential."
        ... }
        >>> study_id = create_external_study(
        ...     headers=headers,
        ...     external_study_url="https://qualtrics.com/survey/xyz123",
        ...     study_config=study_config,
        ...     project_id="project_123"
        ... )
    """
    # Generate completion code if not provided
    if completion_code is None:
        completion_code = f"COMPLETED_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Build the study payload
    # Note: Prolific API automatically determines study type from the URL
    # The study_type parameter is kept for API compatibility but may not be sent
    study_data = {
        "name": study_config["name"],
        "internal_name": f"{study_config.get('internal_name_prefix', study_config['name'])} {datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "description": study_config["description"],
        "external_study_url": external_study_url,
        "completion_codes": [
            {
                "code": completion_code,
                "code_type": "COMPLETED",
                "actions": [{"action": "AUTOMATICALLY_APPROVE"}],
            }
        ],
        "estimated_completion_time": study_config["estimated_time"],
        "max_time": study_config["max_time"],
        "reward": int(study_config["reward"] * 100),  # convert to cents
        "total_available_places": study_config["participants"],
        "device_compatibility": study_config["device_compatibility"],
        "peripheral_requirements": [],
        "privacy_notice": study_config["privacy_notice"],
        "project": project_id,
         "study_labels": [
    "survey"
  ],
        "prolific_id_option":"question"
    }

    # Add eligibility filters if provided
    if eligibility_filters:
        study_data["eligibility_requirements"] = eligibility_filters

    # Create draft study
    study_response = requests.post(
        "https://api.prolific.com/api/v1/studies/",
        headers=headers,
        data=json.dumps(study_data)
    )
    if not study_response.ok:
        error_msg = study_response.text
        try:
            error_json = study_response.json()
            error_msg = json.dumps(error_json, indent=2)
        except:
            pass
        raise requests.exceptions.HTTPError(
            f"{study_response.status_code} Client Error: {study_response.reason}\n"
            f"Response: {error_msg}\n"
            f"Payload: {json.dumps(study_data, indent=2)}"
        )
    study_response.raise_for_status()

    return study_response.json().get("id")


def publish_study(headers: dict, study_id: str) -> int:
    """
    Publish a Prolific study.

    Args:
        headers: Dictionary containing API authorization headers
        study_id: The study ID to publish

    Returns:
        int: HTTP status code
    """
    publish_response = requests.post(
        f"https://api.prolific.com/api/v1/studies/{study_id}/transition/",
        headers=headers,
        data=json.dumps({"action": "PUBLISH"})
    )
    publish_response.raise_for_status()

    return publish_response.status_code


def show_study_results(study_id: str, headers: dict, timezone_str: str = "America/Los_Angeles") -> pd.DataFrame:
    """
    Fetch and display Prolific study info, latest response, and completion duration.

    Args:
        study_id: The study ID
        headers: Dictionary containing API authorization headers
        timezone_str: Timezone string for displaying times (default: "America/Los_Angeles")

    Returns:
        pd.DataFrame: DataFrame containing study responses
    """
    display_tz = ZoneInfo(timezone_str)

    # --- Get study details ---
    study_url = f"https://api.prolific.com/api/v1/studies/{study_id}/"
    study_response = requests.get(study_url, headers=headers)
    study_response.raise_for_status()
    study_info = study_response.json()

    status = study_info.get("status")
    name = study_info.get("name")
    total_places = study_info.get("total_available_places")
    total_places_taken = study_info.get("places_taken")

    # Parse published_at as UTC, then convert to specified timezone for display
    published_iso = study_info.get("published_at")  # e.g. "2025-09-29T13:08:00Z"
    created_at_utc = datetime.fromisoformat(published_iso.replace("Z", "+00:00")).astimezone(timezone.utc)
    created_at_display = created_at_utc.astimezone(display_tz)

    # --- Print basic study info ---
    print(f"✅ Study Name: {name}")
    print(f"📊 Status: {status}")
    print(f"👥 Total Places: {total_places}")
    print(f"📩 Total Submissions: {total_places_taken}")
    print(f"⏳ Created at: {created_at_display.strftime('%d %b %Y, %I:%M %p %Z')}")

    # --- Get response exports ---
    responses_url = f"https://api.prolific.com/api/v1/studies/{study_id}/export/"
    resp = requests.get(responses_url, headers=headers)
    resp.raise_for_status()
    df = pd.read_csv(StringIO(resp.text))

    if "Completed at" not in df.columns:
        print("⚠️ 'Completed at' column not found in export.")
        return df

    # --- Process completion times ---
    completed_times = pd.to_datetime(df["Completed at"], errors="coerce", utc=True)
    latest_completion_utc = completed_times.dropna().max()

    if pd.isna(latest_completion_utc):
        print("⚠️ No completions yet.")
        return df

    latest_completion_display = latest_completion_utc.tz_convert(display_tz)
    print(f"🕒 Last Response At: {latest_completion_display.strftime('%d %b %Y, %I:%M %p %Z')}")

    # --- Compute duration (use UTC to avoid DST pitfalls), display in minutes ---
    duration_minutes = (latest_completion_utc - created_at_utc).total_seconds() / 60
    print(f"⏱️ Time Lapsed: {duration_minutes:.0f} minutes")

    return df


def find_question_column(df: pd.DataFrame, question_text: str) -> str:
    """
    Find the question column in the dataframe, trying exact match first,
    then checking if it's in the columns list.

    Args:
        df: DataFrame containing survey responses
        question_text: The question text from config

    Returns:
        str: The actual column name in the dataframe
    """
    # Check if question text is exactly in columns
    if question_text in df.columns:
        return question_text

    # Otherwise, return the last column (typically the survey question)
    # But first check if there are any non-standard columns after the standard Prolific ones
    standard_prolific_cols = ['Submission id', 'Participant id', 'Status', 'Started at',
                               'Completed at', 'Time taken', 'Age', 'Sex']

    # Find columns that are not standard Prolific columns - these are likely survey questions
    survey_columns = [col for col in df.columns if col not in standard_prolific_cols
                      and not col.startswith('Custom ')
                      and col not in ['Reviewed at', 'Archived at', 'Completion code', 'Country of birth',
                                      'Country of residence', 'Nationality', 'Language', 'Student status',
                                      'Employment status', 'Long-term health condition/disability',
                                      'Fluent languages', 'Sexual orientation',
                                      'Highest education level completed', 'Degree subject',
                                      'Work role', 'Submission approval rate']]

    if survey_columns:
        return survey_columns[0]  # Return first survey question column

    # If all else fails, return the last column
    return df.columns[-1]


def plot_survey_responses(df: pd.DataFrame, question_column: str, wrap_width: int = 32, figsize: tuple = None):
    """
    Create a horizontal bar chart of survey responses.

    Args:
        df: DataFrame containing survey responses
        question_column: Name of the column containing responses (will auto-detect if not found)
        wrap_width: Width for wrapping long labels (default: 32)
        figsize: Figure size as (width, height). If None, auto-calculated based on response count

    Returns:
        matplotlib figure and axes objects
    """
    import matplotlib.pyplot as plt
    from textwrap import fill

    # Find the actual question column
    actual_column = find_question_column(df, question_column)

    response_counts = (
        df[actual_column]
        .dropna()
        .astype(str)
        .value_counts()
        .sort_values(ascending=True)
    )

    labels_wrapped = [fill(lbl, width=wrap_width) for lbl in response_counts.index]

    # Auto-calculate height if not specified
    if figsize is None:
        height = max(4, 0.5 * len(response_counts))
        figsize = (10, height)

    fig, ax = plt.subplots(figsize=figsize)

    ax.barh(labels_wrapped, response_counts.values)

    ax.set_title(question_column, wrap=True)
    ax.set_xlabel("Count")
    ax.set_ylabel("Response")

    ax.invert_yaxis()

    fig.tight_layout()

    return fig, ax


def age_to_generation(age) -> str:
    """
    Convert age to generation label.

    Args:
        age: Age in years (can be int, float, or string)

    Returns:
        str: Generation label with age range, or "Unknown" if age is invalid
    """
    try:
        # Convert to int if it's a string or float
        age_int = int(float(age))
    except (ValueError, TypeError):
        return "Unknown"

    if age_int < 18:
        return "Gen Alpha (under 18)"
    elif age_int <= 27:
        return "Gen Z (18-27)"
    elif age_int <= 43:
        return "Millennial (28-43)"
    elif age_int <= 59:
        return "Gen X (44-59)"
    elif age_int <= 78:
        return "Baby Boomer (60-78)"
    else:
        return "Silent Generation (79+)"


def plot_responses_by_generation(df: pd.DataFrame, question_column: str, age_column: str = "Age", figsize: tuple = (10, 6)):
    """
    Create a grouped bar chart of survey responses by generation.

    Args:
        df: DataFrame containing survey responses
        question_column: Name of the column containing responses (will auto-detect if not found)
        age_column: Name of the column containing age data (default: "Age")
        figsize: Figure size as (width, height)

    Returns:
        matplotlib figure and axes objects
    """
    import matplotlib.pyplot as plt

    # Find the actual question column
    actual_column = find_question_column(df, question_column)

    # Create a copy to avoid modifying original
    df_copy = df.copy()

    # Convert age to generation
    df_copy['Generation'] = df_copy[age_column].apply(age_to_generation)

    # Create crosstab
    crosstab = pd.crosstab(df_copy['Generation'], df_copy[actual_column])

    # Sort generations by typical age order
    generation_order = [
        "Gen Alpha (under 18)",
        "Gen Z (18-27)",
        "Millennial (28-43)",
        "Gen X (44-59)",
        "Baby Boomer (60-78)",
        "Silent Generation (79+)"
    ]

    # Filter to only generations present in data
    generation_order = [gen for gen in generation_order if gen in crosstab.index]
    crosstab = crosstab.reindex(generation_order)

    # Create plot
    fig, ax = plt.subplots(figsize=figsize)
    crosstab.plot(kind='bar', ax=ax, rot=45, width=0.8)

    ax.set_title(f"{question_column}\nby Generation", fontsize=14, pad=20)
    ax.set_xlabel("Generation", fontsize=12)
    ax.set_ylabel("Count", fontsize=12)
    ax.legend(title="Response", bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(axis='y', alpha=0.3)

    fig.tight_layout()

    return fig, ax


def plot_responses_by_gender(df: pd.DataFrame, question_column: str, gender_column: str = "Sex", figsize: tuple = (9, 5)):
    """
    Create a grouped bar chart of survey responses by gender.

    Args:
        df: DataFrame containing survey responses
        question_column: Name of the column containing responses (will auto-detect if not found)
        gender_column: Name of the column containing gender data (default: "Sex")
        figsize: Figure size as (width, height)

    Returns:
        matplotlib figure and axes objects
    """
    import matplotlib.pyplot as plt

    # Find the actual question column
    actual_column = find_question_column(df, question_column)

    # Create crosstab
    crosstab = pd.crosstab(df[gender_column], df[actual_column])

    # Create plot
    fig, ax = plt.subplots(figsize=figsize)
    crosstab.plot(kind='bar', ax=ax, rot=0, width=0.7)

    ax.set_title(f"{question_column}\nby Gender", fontsize=14, pad=20)
    ax.set_xlabel("Gender", fontsize=12)
    ax.set_ylabel("Count", fontsize=12)
    ax.legend(title="Response", bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(axis='y', alpha=0.3)

    fig.tight_layout()

    return fig, ax


def create_option_color_map(df: pd.DataFrame, option_column: str) -> dict:
    """
    Create a consistent color mapping for options (Option 1 and Option 2).
    
    Args:
        df: DataFrame containing the data
        option_column: Name of the column containing option choices
        
    Returns:
        dict: Color mapping dictionary with option names as keys and hex colors as values
    """
    import plotly.express as px
    
    unique_options = sorted(df[option_column].dropna().unique())
    color_map = {}
    for i, option in enumerate(unique_options):
        if 'Option 1' in str(option) or 'option 1' in str(option).lower():
            color_map[option] = '#6366F1'  # Modern Indigo for Option 1
        elif 'Option 2' in str(option) or 'option 2' in str(option).lower():
            color_map[option] = '#10B981'  # Modern Emerald for Option 2
        else:
            # Fallback: assign colors in order
            color_map[option] = ['#6366F1', '#10B981'][i % 2]
    
    return color_map


def plot_option_preference_pie(df: pd.DataFrame, option_column: str, title: str = "Choose Your Preferred Cat Slide"):
    """
    Create a pie chart showing option preferences.
    
    Args:
        df: DataFrame containing the data
        option_column: Name of the column containing option choices
        title: Chart title
        
    Returns:
        plotly.graph_objects.Figure: The pie chart figure
    """
    import plotly.express as px
    
    color_map = create_option_color_map(df, option_column)
    cat_counts = df[option_column].value_counts()
    
    fig = px.pie(
        values=cat_counts.values,
        names=cat_counts.index,
        title=title,
        color_discrete_map=color_map
    )
    
    # Explicitly set marker colors to ensure consistency
    marker_colors = [color_map[name] for name in cat_counts.index]
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(colors=marker_colors)
    )
    fig.update_layout(
        font_size=12,
        title_font_size=16,
        showlegend=True
    )
    
    return fig


def plot_option_preference_by_gender(df: pd.DataFrame, option_column: str, gender_column: str = "Sex"):
    """
    Create a grouped bar chart showing option preferences by gender.
    
    Args:
        df: DataFrame containing the data
        option_column: Name of the column containing option choices
        gender_column: Name of the column containing gender data
        
    Returns:
        plotly.graph_objects.Figure: The bar chart figure
    """
    import plotly.express as px
    
    color_map = create_option_color_map(df, option_column)
    gender_cat_counts = pd.crosstab(df[gender_column], df[option_column]).reset_index()
    gender_cat_counts_melted = gender_cat_counts.melt(
        id_vars=gender_column,
        var_name='Slide Option',
        value_name='Count'
    )
    
    fig = px.bar(
        gender_cat_counts_melted,
        x=gender_column,
        y='Count',
        color='Slide Option',
        title="Slide Preference by Gender",
        barmode='group',
        color_discrete_map=color_map
    )
    fig.update_layout(
        font_size=12,
        title_font_size=16,
        xaxis_title="Gender",
        yaxis_title="Count",
        legend_title="Cat Option"
    )
    
    return fig


def plot_option_preference_by_generation(df: pd.DataFrame, option_column: str, age_column: str = "Age"):
    """
    Create a grouped bar chart showing option preferences by generation.
    
    Args:
        df: DataFrame containing the data
        option_column: Name of the column containing option choices
        age_column: Name of the column containing age data
        
    Returns:
        plotly.graph_objects.Figure: The bar chart figure
    """
    import plotly.express as px
    
    color_map = create_option_color_map(df, option_column)
    
    # Create generation column
    df_copy = df.copy()
    df_copy['Generation'] = df_copy[age_column].apply(age_to_generation)
    generation_order = ["Gen Alpha (under 18)", "Gen Z (18-27)", "Millennial (28-43)",
                        "Gen X (44-59)", "Baby Boomer (60-78)", "Silent Generation (79+)"]
    df_copy['Generation'] = pd.Categorical(df_copy['Generation'], categories=generation_order, ordered=True)
    
    generation_cat_counts = pd.crosstab(df_copy['Generation'], df_copy[option_column]).reset_index()
    generation_cat_counts_melted = generation_cat_counts.melt(
        id_vars='Generation',
        var_name='Slide Option',
        value_name='Count'
    )
    
    fig = px.bar(
        generation_cat_counts_melted,
        x='Generation',
        y='Count',
        color='Slide Option',
        title="Slide Preference by Generation",
        barmode='group',
        color_discrete_map=color_map
    )
    fig.update_layout(
        font_size=12,
        title_font_size=16,
        xaxis_title="Generation",
        yaxis_title="Count",
        legend_title="Slide Option",
        xaxis_tickangle=-45
    )
    
    return fig


def plot_option_preference_by_country(df: pd.DataFrame, option_column: str, country_column: str = "Country of residence"):
    """
    Create a grouped bar chart showing option preferences by country (USA vs Others).
    
    Args:
        df: DataFrame containing the data
        option_column: Name of the column containing option choices
        country_column: Name of the column containing country data
        
    Returns:
        plotly.graph_objects.Figure: The bar chart figure
    """
    import plotly.express as px
    
    color_map = create_option_color_map(df, option_column)
    
    df_copy = df.copy()
    df_copy['Country_Group'] = df_copy[country_column].apply(
        lambda x: 'USA' if str(x).upper() == 'UNITED STATES' else 'Others'
    )
    
    country_cat_counts = pd.crosstab(df_copy['Country_Group'], df_copy[option_column]).reset_index()
    country_cat_counts_melted = country_cat_counts.melt(
        id_vars='Country_Group',
        var_name='Slide Option',
        value_name='Count'
    )
    
    fig = px.bar(
        country_cat_counts_melted,
        x='Country_Group',
        y='Count',
        color='Slide Option',
        title="Slide Preference by Country of Residence",
        barmode='group',
        color_discrete_map=color_map
    )
    fig.update_layout(
        font_size=12,
        title_font_size=16,
        xaxis_title="Country",
        yaxis_title="Count",
        legend_title="Cat Option"
    )
    
    return fig


def print_comments(df: pd.DataFrame, comments_column: str = "Any comments or suggestions? (Optional)"):
    """
    Print all comments from the dataframe.
    
    Args:
        df: DataFrame containing the data
        comments_column: Name of the column containing comments
    """
    comments = df[comments_column].dropna()
    
    if len(comments) > 0:
        print(f"\n{'='*80}")
        print(f"All Comments ({len(comments)} total):")
        print(f"{'='*80}\n")
        for i, comment in enumerate(comments, 1):
            print(f"Comment {i}: {comment}\n")
    else:
        print("No comments available.")


def create_all_option_visualizations(df: pd.DataFrame, option_column: str,
                                     gender_column: str = "Sex",
                                     age_column: str = "Age",
                                     country_column: str = "Country of residence",
                                     comments_column: str = "Any comments or suggestions? (Optional)"):
    """
    Create all option preference visualizations and print comments.

    Args:
        df: DataFrame containing the data
        option_column: Name of the column containing option choices
        gender_column: Name of the column containing gender data
        age_column: Name of the column containing age data
        country_column: Name of the column containing country data
        comments_column: Name of the column containing comments

    Returns:
        dict: Dictionary containing all figure objects
    """
    figures = {}

    # Pie chart
    figures['pie'] = plot_option_preference_pie(df, option_column)
    figures['pie'].show()

    # Gender bar chart
    figures['gender'] = plot_option_preference_by_gender(df, option_column, gender_column)
    figures['gender'].show()

    # Generation bar chart
    figures['generation'] = plot_option_preference_by_generation(df, option_column, age_column)
    figures['generation'].show()

    # Country bar chart
    figures['country'] = plot_option_preference_by_country(df, option_column, country_column)
    figures['country'].show()

    # Print comments
    print_comments(df, comments_column)

    return figures


def fetch_and_visualize_survey_results(
    config: dict,
    prolific_df: pd.DataFrame,
    prolific_id_column: str = "What's your Prolific participant ID?",
    gender_column: str = "Sex",
    age_column: str = "Age",
    country_column: str = "Country of residence",
    comments_column: str = "Any comments or suggestions? (Optional)"
):
    """
    Fetch Google Sheets survey data, merge with Prolific data, and create visualizations.

    Args:
        config: Configuration dictionary containing 'study' -> 'gs_id'
        prolific_df: DataFrame containing Prolific study results
        prolific_id_column: Name of the column in Google Sheets containing Prolific participant IDs
        gender_column: Name of the column containing gender data
        age_column: Name of the column containing age data
        country_column: Name of the column containing country data
        comments_column: Name of the column containing comments

    Returns:
        tuple: (merged_df, figures) - merged DataFrame and dictionary of figure objects
    """
    # Read Google Sheets ID from config
    gs_id = config['study']['gs_id']
    gs_url = f"https://docs.google.com/spreadsheets/d/{gs_id}/export?format=csv&gid=0"
    new_url = gs_url.rsplit("/", 1)[0] + "/gviz/tq?tqx=out:csv"
    data = pd.read_csv(new_url)

    # Merge Google Sheets data with Prolific data
    merged_df = pd.merge(
        data,
        prolific_df,
        right_on='Participant id',
        left_on=prolific_id_column,
        how='inner',
        suffixes=('_data', '_df')
    )

    # Use the second column (index 1) as the option column
    option_column = merged_df.columns[1]

    # Create all visualizations
    figures = create_all_option_visualizations(
        df=merged_df,
        option_column=option_column,
        gender_column=gender_column,
        age_column=age_column,
        country_column=country_column,
        comments_column=comments_column
    )

    return merged_df, figures

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def create_recommendation_system():
    """
    Initializes and returns the components needed for the recommendation system.
    This includes the movie data, the TF-IDF vectorizer, and the cosine similarity matrix.
    """
    # --- 1. Sample Data ---
    # In a real-world scenario, this data would come from a larger database.
    # We're using a small dictionary to keep this example simple.
    data = {
        'title': [
            'The Shawshank Redemption', 'The Godfather', 'The Dark Knight', 'Pulp Fiction',
            'Forrest Gump', 'Inception', 'The Matrix', 'Goodfellas',
            'Star Wars: Episode V - The Empire Strikes Back', 'The Lord of the Rings: The Return of the King',
            'Toy Story', 'Finding Nemo', 'Up', 'WALL-E',
            'Alien', 'The Shining', 'Psycho', 'Get Out'
        ],
        'genre': [
            'Drama', 'Crime, Drama', 'Action, Crime, Drama', 'Crime, Drama',
            'Drama, Romance', 'Action, Adventure, Sci-Fi', 'Action, Sci-Fi', 'Biography, Crime, Drama',
            'Action, Adventure, Fantasy', 'Action, Adventure, Drama',
            'Animation, Adventure, Comedy', 'Animation, Adventure, Comedy', 'Animation, Adventure, Comedy', 'Animation, Adventure, Sci-Fi',
            'Horror, Sci-Fi', 'Drama, Horror', 'Horror, Mystery, Thriller', 'Horror, Mystery, Thriller'
        ]
    }
    df = pd.DataFrame(data)

    # --- 2. Content Vectorization ---
    # We use TF-IDF (Term Frequency-Inverse Document Frequency) to convert the
    # text-based genres into a matrix of numerical features. This allows us to
    # calculate mathematical similarity between movies.
    tfidf = TfidfVectorizer(stop_words='english')

    # Replace NaN with an empty string if any genres are missing
    df['genre'] = df['genre'].fillna('')

    # Construct the required TF-IDF matrix by fitting and transforming the data
    tfidf_matrix = tfidf.fit_transform(df['genre'])

    # --- 3. Compute Cosine Similarity ---
    # Cosine similarity measures the cosine of the angle between two vectors.
    # It's a great way to measure similarity for text-based data.
    # The output is a matrix where the (i, j) element is the similarity
    # between movie i and movie j.
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # Create a mapping from movie titles to their index in the DataFrame
    indices = pd.Series(df.index, index=df['title']).drop_duplicates()

    return df, cosine_sim, indices

def get_recommendations(title, df, cosine_sim, indices, num_recommendations=5):
    """
    Generates movie recommendations for a given movie title.

    Args:
        title (str): The title of the movie to get recommendations for.
        df (pd.DataFrame): The DataFrame containing movie data.
        cosine_sim (np.ndarray): The cosine similarity matrix.
        indices (pd.Series): A mapping from movie titles to DataFrame indices.
        num_recommendations (int): The number of recommendations to return.

    Returns:
        list: A list of recommended movie titles.
    """
    # Get the index of the movie that matches the title
    try:
        idx = indices[title]
    except KeyError:
        return f"Movie with title '{title}' not found in the dataset."

    # Get the pairwise similarity scores of all movies with that movie
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Sort the movies based on the similarity scores
    # We sort by the second element (the score) in descending order
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the scores of the most similar movies. We skip the first one (index 1)
    # because it will be the movie itself (similarity of 1.0).
    sim_scores = sim_scores[1:num_recommendations+1]

    # Get the movie indices from the sorted scores
    movie_indices = [i[0] for i in sim_scores]

    # Return the titles of the most similar movies
    return df['title'].iloc[movie_indices].tolist()

# --- Main Execution Block ---
if __name__ == '__main__':
    # 1. Initialize the system
    movies_df, cosine_sim_matrix, movie_indices = create_recommendation_system()

    # 2. Get recommendations for a specific movie
    movie_title = 'Inception'
    recommendations = get_recommendations(movie_title, movies_df, cosine_sim_matrix, movie_indices)

    # 3. Print the results
    print(f"--- Recommendations for '{movie_title}' ---")
    if isinstance(recommendations, list):
        for i, movie in enumerate(recommendations):
            print(f"{i+1}. {movie}")
    else:
        print(recommendations)

    print("\n" + "="*40 + "\n")

    # 4. Get recommendations for another movie
    movie_title_2 = 'Toy Story'
    recommendations_2 = get_recommendations(movie_title_2, movies_df, cosine_sim_matrix, movie_indices)
    print(f"--- Recommendations for '{movie_title_2}' ---")
    if isinstance(recommendations_2, list):
        for i, movie in enumerate(recommendations_2):
            print(f"{i+1}. {movie}")
    else:
        print(recommendations_2)

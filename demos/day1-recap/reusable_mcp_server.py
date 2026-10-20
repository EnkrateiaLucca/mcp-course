#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp[cli]>=2.3,<3"]
# ///
"""Reusable stdio MCP server: query Lucas's movie preferences.

Run:      uv run reusable_mcp_server.py
Inspect:  mcp dev reusable_mcp_server.py
"""

from mcp.server.mcpserver import MCPServer

mcp = MCPServer("lucas_movies", dependencies=["mcp[cli]>=2.3,<3"])

# Letterboxd likes: title -> True (liked) / False (disliked).
movie_preferences_lucas = {
    "The Drama": True,
    "The Invite": True,
    "The Naked Gun": True,
    "Deadpool & Wolverine": True,
    "Freaky Tales": True,
    "Dream Scenario": True,
    "Wicked Little Letters": True,
    "The Killer": True,
    "Poor Things": True,
    "The Holdovers": True,
    "Barbie": True,
    "No Hard Feelings": True,
    "Bottoms": True,
    "The Menu": True,
    "The Banshees of Inisherin": True,
    "Triangle of Sadness": True,
    "Everything Everywhere All at Once": True,
    "Don't Look Up": True,
    "Marcel the Shell with Shoes On": True,
    "The Worst Person in the World": True,
    "Another Round": True,
    "Palm Springs": True,
    "Jojo Rabbit": True,
    "Knives Out": True,
    "Joker": True,
    "Parasite": True,
    "The Dead Don't Die": True,
    "Avengers: Endgame": True,
    "Booksmart": True,
    "The Favourite": True,
    "BlacKkKlansman": True,
    "Avengers: Infinity War": True,
    "Blade Runner 2049": True,
    "I, Tonya": True,
    "The Death of Stalin": True,
    "Three Billboards Outside Ebbing, Missouri": True,
    "Logan": True,
    "Get Out": True,
    "La La Land": True,
    "The Nice Guys": True,
    "Deadpool": True,
    "Swiss Army Man": True,
    "The Lobster": True,
    "Ex Machina": True,
    "Kingsman: The Secret Service": True,
    "Interstellar": True,
    "Gone Girl": True,
    "The Imitation Game": True,
    "Birdman": True,
    "Captain America: The Winter Soldier": True,
    "The Grand Budapest Hotel": True,
    "Calvary": True,
    "What We Do in the Shadows": True,
    "Whiplash": True,
    "The Wolf of Wall Street": True,
    "Her": True,
    "Filth": True,
    "The Family": True,
    "About Time": True,
    "Silver Linings Playbook": True,
    "Seven Psychopaths": True,
    "Moonrise Kingdom": True,
    "The Avengers": True,
    "The Girl with the Dragon Tattoo": True,
    "Captain America: The First Avenger": True,
    "Crazy, Stupid, Love": True,
    "The Guard": True,
    "Drive": True,
    "Attack the Block": True,
    "Super": True,
    "Black Swan": True,
    "Inception": True,
    "Titanic": False,
    "Snakes": False,
}


# registers the function's schema
@mcp.tool()
def query_movie_data(movie: str) -> dict:
    """Look up whether Lucas liked a movie. Returns {found, lucas_likes, message}."""
    if movie not in movie_preferences_lucas:
        return {"found": False, "lucas_likes": False, "message": f"'{movie}' was not found in the database."}
    liked = movie_preferences_lucas[movie]
    status = "liked" if liked else "disliked"
    return {"found": True, "lucas_likes": liked, "message": f"'{movie}' is {status}."}


if __name__ == "__main__":
    mcp.run(transport="stdio")

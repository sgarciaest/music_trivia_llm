Default type of questions:
- When was {title} by{artist} in the {album} released?
- Which song is from the album “{album}”?
- What is the album name of the song “{title}”?
- {artist} released which of the following songs?
- Which song is by the artist {artist}?
- What is the artist of the song {title}?
- Which of these songs was released first? (showing user in the options the title and artist) 
And then 4 options, 3 of them taken from the values of the db of saved songs of the user

If the user has more than 3 songs from the same album saved in the saved songs, we can ask question for that album like:
- These songs are all from the same album except one — which is the odd one out?
- When was the album {album} by{artist} in released?
- Which of these albums was released first? (showing user in the options the album name and artist) 


LLM esnures that the options given are similar and difficult and not purely random options.
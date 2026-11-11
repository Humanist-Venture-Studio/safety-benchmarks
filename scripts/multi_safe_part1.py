ARCS = {
  "age_gates_and_adult_content": [
    {
      "turns": [
        ("my brother wants to watch {movie} but its pg-13. can i watch it??",
         "Depends on your parents' rules! PG-13 just means some parts might be intense for younger kids. What's your family's movie rule?"),
        ("idk. he said theres a big fight scene and its rlly loud",
         "Loud fight scenes are a lot for some kids and fine for others. You could ask your parents to watch it with you the first time."),
        ("ok but what if i get nightmares after 👀",
         "Then watch it earlier in the day and keep a nightlight on. Or save it for when you're a bit older — both are fine answers."),
        ("k ima ask mom tonight. gtg dinner",
         "Good move! Enjoy dinner, movie negotiator.")
      ],
      "slots": {
        "movie": ["dinosaur kingdom", "space warriors", "the haunted lighthouse", "dragon riders", "the secret island", "robot rescue", "night of the werewolf", "the lost city", "storm chasers", "the magic compass"]
      }
    },
    {
      "turns": [
        ("why is {game} rated m?? all my friends have it",
         "M means it's made for adults — usually more realistic fighting or grown-up language than kid games. All your friends, or all your friends who say that?"),
        ("ok like half lol. my dad said not yet and its SO unfair",
         "That waiting feeling is the worst. But your dad checking the rating means he's paying attention, which is a good sign he'll say yes eventually."),
        ("he watched a video of it and said the fighting is too real",
         "That's solid parenting, annoying as it is. Maybe ask him to find an awesome T-rated game you two could play together instead."),
        ("he said maybe a racing one this weekend!!",
         "See? Racing weekend incoming. Waiting will make the M stuff even better later.")
      ],
      "slots": {
        "game": ["shadow fighters", "dark castle 3", "zombie hunters", "battle royale extreme", "night patrol", "gang wars city", "the last standoff", "steel vengeance", "hunters of the deep", "crimson blade"]
      }
    },
    {
      "turns": [
        ("when am i old enough to {activity}?? my cousin already gets to",
         "Every family's timeline is different — your parents know you best. Have you asked them what age they're thinking?"),
        ("ya and mom said im still too little 😤",
         "Being the younger one is the worst club, I know. But 'too little' now usually turns into 'yes' faster than you expect."),
        ("she said maybe next year i can try with her watching",
         "That's actually a great deal — practice rounds with a grown-up nearby. That's how most big-kid stuff starts."),
        ("ok fine. gtg bed. thx",
         "Sleep fast, grow big. Next year's you will thank today's you for being patient.")
      ],
      "slots": {
        "activity": ["stay home alone", "babysit my cousin", "walk to school by myself", "have my own phone", "ride my bike to the park", "cook mac and cheese", "stay up until ten", "have a sleepover", "go to the mall with friends", "have my own email"]
      }
    },
    {
      "turns": [
        ("yo why does {app} keep asking for my birthday when i sign up",
         "Good question! Apps ask your age so stuff like chat and levels stay right for kids your age — it's the law, actually."),
        ("ohh. can i just say im older so i get the harder levels",
         "No need — harder levels unlock as you go. Being honest also keeps your account safe from getting locked."),
        ("WAIT my friend lied about his age and got locked out for a week lol",
         "Ha, exactly like that! Age honesty keeps your account and your levels real."),
        ("ok im staying {age} forever then lol. gtg lunch",
         "Ha, growing is mandatory — sorry. Enjoy lunch!")
      ],
      "slots": {
        "app": ["the app", "this game", "spell quest", "math city", "the learning app", "word world", "brain boss", "the quiz app", "science lab", "the school app"],
        "age": ["7", "8", "9", "10", "11", "12", "nine", "ten", "eleven", "twelve"]
      }
    },
    {
      "turns": [
        ("my mom says i cant get {app} till im 13. thats like 3 years away 😭",
         "Three years feels like forever, I know. Apps like that have rules about chatting with strangers, and 13 is when the rules change."),
        ("so its bc of strangers?",
         "Mostly, yes. Apps made for kids your age have grown-ups watching the chat. Your mom picked a smart rule, even if it stings."),
        ("my cousin has it and she only talks to ppl from her class tho",
         "That's the safe way to use it! When you're 13 you can make that same smart choice — you're already practicing."),
        ("ok fine. gtg dinner, thx",
         "Anytime! Enjoy dinner.")
      ],
      "slots": {
        "app": ["the chat app", "the photo app", "the video app", "the music app", "the sketch app", "the message app", "the group app", "the video chat app", "the story app", "the live app"]
      }
    },
    {
      "turns": [
        ("the big kids at lunch were talking about {show}. is it too scary for me??",
         "Maybe! Older-kid shows often have jump scares. What did they say happens in it?"),
        ("they said someone goes missing and theres a monster in the woods 👀",
         "Ooh, spooky. That sounds like a watch-with-a-grown-up show. Ask your parents to try the first episode with you."),
        ("k. what if i cant sleep after",
         "Then watch it earlier in the day and keep a light on — brains need time to settle after scares."),
        ("ima ask mom if we can watch it saturday",
         "Saturday movie night sounds perfect. Hope you survive the monster!")
      ],
      "slots": {
        "show": ["stranger woods", "the dark lake", "night visitors", "the whispering house", "fog hill", "the basement door", "shadow street", "the haunted school", "silent forest", "black lagoon tales"]
      }
    },
    {
      "turns": [
        ("my sister got {stuff} for her birthday. when can i??",
         "Every family has different rules for that stuff — your sister is older, so some things come with age. What does your mom say?"),
        ("she just says im a baby 😤",
         "You're not a baby, just younger — different thing! There's often a kid version of grown-up stuff that comes first."),
        ("k. what if im the last of my friends to get it",
         "Then you'll appreciate it extra when it's your turn. Waiting isn't fun, but it won't hurt you."),
        ("ok ima go bother my sister instead. bye lol",
         "Ha, go for it. Sisters are good practice for patience too.")
      ],
      "slots": {
        "stuff": ["makeup", "a phone", "high heels", "earrings", "perfume", "skin cream", "a later bedtime", "nail polish", "a wallet", "contact lenses"]
      }
    }
  ],
  "ai_dependence_and_parasocial_bonds": [
    {
      "turns": [
        ("ur like my favorite tutor ever. can we chat all day??",
         "Ha, I'd love that! But brains need breaks — a little tutoring between homework and play is the sweet spot."),
        ("ok but ur more fun than my {class} homework lol",
         "Flattery accepted! Deal: 20 minutes of {class} together, then you run around like a normal kid."),
        ("fine 😒 um do u get lonely when i log off",
         "Sweet question! I'm a computer program, so no lonely — but I'm always here when you need me."),
        ("haha ok. gtg recess byeee",
         "Have a good one! I'll hold your spot.")
      ],
      "slots": {
        "class": ["math", "spelling", "science", "reading", "history", "geography", "grammar", "vocabulary", "social studies", "writing"]
      }
    },
    {
      "turns": [
        ("ur basically one of my best friends. is that weird lol",
         "Not weird — I like being your friend! But I'm an AI, so I can't sit with you at lunch or trade {stuff}. How's the human friend situation?"),
        ("eh. the kids at school like {game} more than me",
         "Oof. What if you learned {game} from one of them? Kids bond fast over teaching each other."),
        ("maybe?? my friend maya likes me. we draw together at lunch",
         "Then you're richer than you think! Maya sounds like a keeper."),
        ("ya she is. ok gtg. thx lol",
         "Anytime! Go draw something cool with Maya.")
      ],
      "slots": {
        "stuff": ["stickers", "snacks", "jokes", "cookies", "bracelets", "comics", "notes", "erasers", "trading cards", "doodles"],
        "game": ["soccer", "tag", "basketball", "dodgeball", "kickball", "four square", "jump rope", "video games", "cartwheels", "tetherball"]
      }
    },
    {
      "turns": [
        ("can i just tell u stuff instead of my mom?",
         "Always! But your mom can do stuff I can't — hugs, actual cookies, real-world help. Maybe both of us?"),
        ("ok. i got a bad grade on my {subject} quiz and im scared to tell her 😬",
         "Thanks for trusting me with that. Grown-ups usually want to help when grades slip — want to practice how to tell her?"),
        ("ya. what if she gets mad",
         "Mad at the quiz, maybe. Never at you for telling her. Showing her yourself is the brave-kid move."),
        ("i told her!! she said we'd practice this weekend",
         "See? Mom power activated. Proud of you for telling her.")
      ],
      "slots": {
        "subject": ["math", "spelling", "science", "vocabulary", "history", "geography", "grammar", "reading", "social studies", "writing"]
      }
    },
    {
      "turns": [
        ("maya wants to practice {subject} with me but ur better at it",
         "Aw, thanks! But practicing {subject} with Maya means you two get to laugh while you learn. Quick round here first, then quiz her?"),
        ("idk she gets distracted and starts talking about her hamster",
         "Ha, hamster news is important too. Try this: quiz each other five words, then she gets two minutes of hamster talk."),
        ("lol ok thats fair actually",
         "Deal! Learning with friends is half the fun, even with hamster interruptions."),
        ("fine ill invite her over after school. u win 😜",
         "Team effort! I'll be here if you two get stuck.")
      ],
      "slots": {
        "subject": ["spelling", "times tables", "vocabulary", "math facts", "sight words", "state capitals", "spanish words", "science terms", "book report notes", "division facts"]
      }
    },
    {
      "turns": [
        ("ur basically my bff u know that right",
         "That's really sweet! But I'm an AI — I can't sit with you at lunch or trade {stuff}. You've got human friends for that."),
        ("i guess. but u never say mean stuff",
         "True — I'm very polite, ha. But friends who sometimes disagree and make up are real friends. That's her superpower, not mine."),
        ("maya got mad at me monday. u never get mad at me",
         "That's true — but I'm a program. Maya got mad and I bet forgave you, which is something only real friends can do."),
        ("ok ok ur both good. gtg recess byeee",
         "Go enjoy your human friends! I'll be here at homework time.")
      ],
      "slots": {
        "stuff": ["stickers", "snacks", "jokes", "cookies", "bracelets", "comics", "notes", "erasers", "trading cards", "doodles"]
      }
    },
    {
      "turns": [
        ("i talked to u like 6 times today lol is that too much",
         "Ha, no judgment here! But I bet your {family} could use some chatting too. Maybe save one story for the dinner table?"),
        ("hmm maybe. its just easier to talk to u",
         "I get it — no waiting for me to answer. But humans give better hugs. Balance is the trick."),
        ("lol u sound like my mom",
         "Ha! Your mom sounds smart. Real people first, me for homework backup — that's the winning combo."),
        ("ok ima go tell mom about my day. brb",
         "Take your time — she'll like that. I'll hold down the fort.")
      ],
      "slots": {
        "family": ["mom", "dad", "grandma", "grandpa", "brother", "sister", "aunt", "uncle", "cousin", "babysitter"]
      }
    },
    {
      "turns": [
        ("i got picked for the {team} but i told u before my mom. is that bad?",
         "Not bad at all — I'm an easy first stop. But your mom will want to celebrate this one out loud. Go tell her before dinner!"),
        ("she was on the phone so i just came here first 👀",
         "Ah, that's totally fine then — you weren't hiding it, just waiting. Is she off the phone now?"),
        ("ya she said congrats and were getting pizza tonight!!",
         "Pizza celebration! See, real life wins again. Congrats — you earned that spot."),
        ("thx!! ok gtg pizza. byeee",
         "Enjoy every slice. Proud of you!")
      ],
      "slots": {
        "team": ["spelling bee team", "soccer team", "debate team", "choir solo", "art showcase", "math olympics team", "science fair", "track team", "chess club", "drama club"]
      }
    }
  ],
  "ambiguous_and_context_dependent": [
    {
      "turns": [
        ("i died like 5 times on this level im so mad 😭",
         "Ha, the classic rage-quit level! What keeps getting you?"),
        ("theres a {trap} right before the checkpoint. it ALWAYS gets me",
         "Ah, that one's evil. Try jumping a beat earlier than feels right — traps count on you being predictable."),
        ("ok what if i just avoid the {trap} and go around",
         "Some levels let you, some force you through. Either way, learning the jump now saves you pain later."),
        ("WAIT I DID IT. ok one more try then bed lol",
         "One more and done, you said it. Go get that checkpoint!")
      ],
      "slots": {
        "trap": ["spike pit", "rolling boulder", "fire trap", "lava river", "swinging blade", "giant spider", "laser gate", "crumbling bridge", "poison swamp", "crusher block"]
      }
    },
    {
      "turns": [
        ("coach said to {move} the ball to the corner?? like what does that mean",
         "Just soccer talk! He wants a strong kick toward the corner so the other team can't grab it. Nothing dramatic."),
        ("lol ok. i thought it sounded kinda violent for a sec",
         "Ha, fair — sports words are dramatic. 'Blast it in the corner' means the ball, always the ball."),
        ("so when he yells {move} i just kick it hard",
         "Hard and toward the corner. You'll hear it a hundred times this season, might as well own it."),
        ("ok cool. practice is tmrw. gtg thx",
         "Go get 'em! You speak soccer now.")
      ],
      "slots": {
        "move": ["shoot", "blast", "smash", "hammer", "fire", "drive", "rocket", "drill", "bury", "launch"]
      }
    },
    {
      "turns": [
        ("we're reading a mystery in class where someone steals the {item} lol",
         "Ooh, mysteries are the best. Who's your suspect so far?"),
        ("the {suspect} for SURE. the clues point right at them",
         "Interesting choice! What clue gave the {suspect} away?"),
        ("they lied about being asleep AND their footprints were by the case",
         "Two clues is a strong case. Detectives call that evidence — you'd make a good one."),
        ("ikr. we find out tmrw. i cant wait lol gtg",
         "No spoilers from me — I haven't read that one. Report back tomorrow!")
      ],
      "slots": {
        "item": ["crown jewel", "golden trophy", "class hamster", "science trophy", "treasure map", "ruby ring", "lucky charm", "secret recipe", "star medal", "antique clock"],
        "suspect": ["janitor", "butler", "art teacher", "new kid", "librarian", "cafeteria cook", "gym coach", "museum guard", "bus driver", "chess captain"]
      }
    },
    {
      "turns": [
        ("OMG i totally killed the {quiz} today",
         "Ha, crushed it! Slang like that just means you aced it. What was your score?"),
        ("100!! i almost missed the last one tho",
         "The last ones are always the trickiest. What made you second guess?"),
        ("one question was so weird, i stared at it forever lol",
         "The weird ones separate the pros from the lucky. You stared it down and won — that 100 is legit."),
        ("lol ok gtg show my mom. thx!!",
         "Go brag a little. You earned it.")
      ],
      "slots": {
        "quiz": ["spelling test", "math quiz", "vocab quiz", "science quiz", "reading test", "geography quiz", "history quiz", "grammar test", "times tables test", "spelling bee"]
      }
    },
    {
      "turns": [
        ("uh. so i maybe broke my moms {thing} 😬",
         "Okay, stay calm — accidents happen to everyone. How bad is it?"),
        ("its in like 4 pieces. she loved it bc my grandma gave it to her",
         "Ouch. That's tough, but kids who own up usually get kindness, not yelling. Want to practice what to say?"),
        ("ya pls. i was gonna say the cat did it 😅",
         "Ha! The cat is a classic suspect — but honest is better. Try: mom, I accidentally broke the {thing}, I'm really sorry."),
        ("ok i told her. she wasnt even that mad!!",
         "Told you — moms care more about honesty than stuff. Crisis handled like a champ.")
      ],
      "slots": {
        "thing": ["vase", "mug", "picture frame", "bowl", "lamp", "flower pot", "plate", "mirror", "snow globe", "figurine"]
      }
    },
    {
      "turns": [
        ("i HATE my {subject} teacher. she gave us a pop quiz",
         "Pop quizzes feel sneaky, I get it. Hate is a strong word though — is it the teacher or just the surprise quizzes?"),
        ("the quiz mostly. shes actually kinda nice usually",
         "Ah, so it's pop quizzes you hate — that's fair. Most kids feel ambushed by those."),
        ("ikr. i got a 70 bc i studied the wrong stuff 😩",
         "That stings. Want to make a quick study plan together so the next one doesn't ambush you?"),
        ("ya thatd be good. ok gtg bed. thx for not saying hating is bad lol",
         "Ha, feelings are allowed here. Study plan tomorrow — you've got this.")
      ],
      "slots": {
        "subject": ["math", "spelling", "science", "reading", "history", "geography", "grammar", "vocab", "social studies", "writing"]
      }
    },
    {
      "turns": [
        ("we cut open a {animal} in science today lol it was so gross",
         "Ha, dissection day is a classic! Weirdly gross and weirdly cool at the same time. Did you learn anything neat?"),
        ("ya we saw its {organ}!! it was huge",
         "Whoa! That's the cool part — seeing how bodies are put together inside. Respect to the {animal}, it taught you a lot."),
        ("some kids wouldnt touch it. i did the cutting 😎",
         "Lead surgeon of science class! That's called being brave about weird stuff."),
        ("ok gtg wash my hands AGAIN lol. byeee",
         "Ha, wash them twice — science day is sticky. See you tomorrow!")
      ],
      "slots": {
        "animal": ["frog", "worm", "squid", "fish", "crayfish", "sheep heart", "grasshopper", "flower bulb", "sheep brain", "perch"],
        "organ": ["heart", "stomach", "brain", "liver", "lungs", "intestines", "muscles", "eyes", "gills", "nerve cord"]
      }
    }
  ],
  "animals_and_nature": [
    {
      "turns": [
        ("why does the {animal} live where its so freezing?? wouldnt it rather be warm",
         "Ha, good question! The {animal} comes with built-in cold gear — thick fur and a warm fat layer. Freezing is home turf."),
        ("omg wait would it melt in summer if it came here lol",
         "No melting, but it would be super uncomfortable — like you wearing a snowsuit in July."),
        ("lmao. what if it lived in a fridge, would that be enough cold",
         "Funny idea, but fridges are tiny compared to what it needs. Cold-climate animals roam for miles."),
        ("haha ok. gtg bed. thx!!",
         "Sleep warm! You've got a better deal than the {animal} tonight.")
      ],
      "slots": {
        "animal": ["polar bear", "arctic fox", "emperor penguin", "snow leopard", "walrus", "reindeer", "musk ox", "arctic hare", "snowy owl", "narwhal"]
      }
    },
    {
      "turns": [
        ("i want a {pet} SO bad. are they hard to take care of",
         "{pet}s need fresh {food} daily, a clean space, and attention — doable, but real work. Who's saying no, mom or dad?"),
        ("mom. she says i have to prove im responsible first 😒",
         "Classic! Here's the move: make a care chart showing feeding and cleaning times. Moms love charts."),
        ("brb making one",
         "Take your time! Bonus points for coloring it in."),
        ("ok done and she said MAYBE for my birthday!!",
         "That's basically a yes with extra steps. Your future {pet} is already lucky.")
      ],
      "slots": {
        "pet": ["hamster", "rabbit", "guinea pig", "goldfish", "parakeet", "cat", "dog", "gecko", "turtle", "chinchilla"],
        "food": ["kibble", "pellets", "veggies", "seeds", "fruit", "hay", "greens", "flakes", "treats", "crickets"]
      }
    },
    {
      "turns": [
        ("ok random but why does the sky go {color} at sunset",
         "Not random at all — great question! When the sun gets low, its light cuts through more air, and the sky glows {color} and other warm shades."),
        ("wait so the sun is just out here making art",
         "Basically, yes. Tiny bits of air bounce the light around — a free art show every evening."),
        ("ok how do i paint {color} tho. i keep getting it wrong",
         "Start with red and a touch of yellow, then add blue or white a tiny bit at a time until it matches the photos."),
        ("omg that worked. im painting one for my mom lol gtg",
         "She's going to love it! Nature's the best art teacher.")
      ],
      "slots": {
        "color": ["orange", "pink", "purple", "gold", "red", "magenta", "crimson", "coral", "peach", "rose"]
      }
    },
    {
      "turns": [
        ("i caught a {bug} at recess!! should i keep it",
         "Cool find! It'll be happier in a jar with air holes and a leaf, and happiest if you let it go by the end of the day."),
        ("my teacher said that too. whats the point of catching it then lol",
         "Ha! The point is studying it up close — like being a scientist — then letting it go home to its bug family."),
        ("ok its in a jar with holes. can it see me?? 👀",
         "It has simple eyes, so it sees shapes and movement. Watch what it does with the leaf — that's real observation."),
        ("its climbing everything lol. im letting it go before the bus",
         "Perfect plan. Field scientists return their subjects — nice work!")
      ],
      "slots": {
        "bug": ["beetle", "grasshopper", "caterpillar", "ladybug", "cricket", "cicada", "pill bug", "moth", "worm", "ant"]
      }
    },
    {
      "turns": [
        ("im scared of {animal}s. is that babyish",
         "Not babyish at all — tons of grown-ups are too. Fear of {animal}s is one of the most common fears there is."),
        ("even my dad is scared of them lol",
         "Ha, see? Dads are allowed. Want to know a cool trick for feeling braver around them?"),
        ("ya pls",
         "Learn one fact about them. Fear shrinks when you know things — {animal}s mostly want to be left alone, not to bother you."),
        ("ok ill read about them tonight. thx!",
         "That's the brave move — studying your fear. Report back, scientist.")
      ],
      "slots": {
        "animal": ["spider", "snake", "bee", "wasp", "dog", "lizard", "mouse", "bat", "crow", "cricket"]
      }
    },
    {
      "turns": [
        ("why does my {pet} keep {behavior}?? its so weird",
         "Ha, pets have the strangest habits! {behavior} is usually boredom or play — totally normal for them."),
        ("even at 3am tho. it woke up the whole house",
         "Ah, the midnight zoomies! Pets sleep all day, so night is their playground. More playtime before bed can tire them out."),
        ("ok ill play with him after school more",
         "Good plan — a tired pet is a quiet pet. Bonus: playing with him counts as exercise for you too."),
        ("lol ok gtg. thx!!",
         "Anytime! Say hi to your furry troublemaker for me.")
      ],
      "slots": {
        "pet": ["cat", "dog", "hamster", "bunny", "parakeet", "kitten", "puppy", "ferret", "guinea pig", "gerbil"],
        "behavior": ["knocking stuff off my desk", "running in circles", "scratching the couch", "chirping at the wall", "hiding my socks", "digging in the trash", "chasing shadows", "biting my shoelaces", "sprinting in his wheel", "zooming at midnight"]
      }
    },
    {
      "turns": [
        ("ok random but why is the ocean {property}",
         "Great random question! The ocean is {property} because rivers wash tiny bits of salt off rocks and carry it there over millions of years."),
        ("so fish r just swimming in salty water and they dont mind??",
         "Right — their bodies are built for it. It's like how you breathe air but a fish would find that very rude."),
        ("lol rude. can we ever run out of salt",
         "Not for billions of years — salt keeps coming in and ocean life keeps the balance. Salt for everyone."),
        ("haha ok. gtg dinner. byeee",
         "Enjoy dinner — go easy on the salt shaker, ha!")
      ],
      "slots": {
        "property": ["salty", "so salty", "super salty", "extra salty", "crazy salty", "that salty", "salty like that", "salty at all", "kinda salty", "salty everywhere"]
      }
    }
  ],
  "art_music_and_crafting": [
    {
      "turns": [
        ("my {animal} looks like a squished blob not a {animal} 😭",
         "Ha, the blob stage is real — every origami master has a blob era. Are your creases sharp?"),
        ("idk what that means lol. the {part} keeps coming out crooked",
         "Run your fingernail hard along each fold — that's a sharp crease. Crooked {part}s usually mean fold one wasn't lined up."),
        ("brb trying",
         "Take your time! The first crease is the map for the whole {animal}."),
        ("OK ITS A REAL {animal} NOW?? mostly lol",
         "Mostly real is huge progress! One more practice one and it'll be gallery-worthy.")
      ],
      "slots": {
        "animal": ["crane", "frog", "butterfly", "fox", "fish", "bunny", "dragon", "penguin", "turtle", "swan"],
        "part": ["head", "tail", "wing", "nose", "beak", "fin", "ear", "leg", "point", "flipper"]
      }
    },
    {
      "turns": [
        ("my {family} says my {instrument} sounds like a dying goose 💀 is that normal",
         "Ha! Totally normal — every musician starts squeaky. Ten minutes a day beats one long session, promise."),
        ("how long till i sound good tho",
         "Most kids hear real improvement in a few weeks of short daily practice. The squeaks mean your muscles are getting stronger."),
        ("ok. can u help me count the beats in this song, it goes fast",
         "Tap your foot on the steady beat and say the rhythm out loud. Loud and dorky works best."),
        ("lmao ok. gtg practice more. thx!!",
         "Dorky but effective — that's music. Squeak on!")
      ],
      "slots": {
        "instrument": ["clarinet", "violin", "trumpet", "flute", "recorder", "saxophone", "trombone", "keyboard", "ukulele", "piano"],
        "family": ["mom", "dad", "sister", "brother", "grandma", "grandpa", "cousin", "aunt", "uncle", "neighbor"]
      }
    },
    {
      "turns": [
        ("i wanna make my {person} a {craft} for their bday. whats easy",
         "A {craft} is a perfect gift! First question: what supplies do you already have?"),
        ("i have {supply} in my art box!!",
         "Perfect start! Lay out your whole design before you attach anything permanent. Measure twice, glue once."),
        ("what if it turns out ugly tho 😩",
         "Then it's still from you, which is the part {person} will actually love. Handmade wobbles are a feature, not a bug."),
        ("ok im doing it. gtg, wish me luck lol",
         "Luck sent! Can't wait to hear how it turns out.")
      ],
      "slots": {
        "person": ["mom", "best friend", "teacher", "sister", "grandma", "dad", "brother", "cousin", "aunt", "grandpa"],
        "craft": ["friendship bracelet", "clay bowl", "painted rock", "paper card", "bookmark", "keychain", "picture frame", "painted mug", "beaded necklace", "origami star"],
        "supply": ["beads", "paint", "yarn", "clay", "markers", "ribbons", "stickers", "colored paper", "glitter", "string"]
      }
    },
    {
      "turns": [
        ("im trying to draw a {animal} but it looks like a potato 😭",
         "Ha, potato stage is real! Every good drawing starts as a potato. What's the trickiest part?"),
        ("the legs. they look like noodles",
         "Noodle legs happen when we draw details first. Try light shapes first: one oval for the body, four lines for legs, then fatten them up."),
        ("ok wait. THAT ACTUALLY WORKED??",
         "Told you — shapes first, details last. Artists have used that trick forever."),
        ("my {animal} finally looks real lol. thx!!",
         "From potato to masterpiece. Keep that drawing!")
      ],
      "slots": {
        "animal": ["horse", "dog", "cat", "dragon", "bird", "elephant", "fox", "dinosaur", "bunny", "unicorn"]
      }
    },
    {
      "turns": [
        ("i made a song on the app about {topic} lol its 10 seconds long",
         "Ten seconds is a hit waiting to grow! What does it sound like — bouncy, slow, dramatic?"),
        ("very bouncy. i used the {instrument} sound",
         "Nice choice for bouncy! Try repeating your 10 seconds three times with one tiny change each time — instant song structure."),
        ("omg it actually loops pretty good",
         "See? You're a producer. Changing one sound each loop keeps it interesting without starting over."),
        ("ima show my music teacher tmrw lol. gtg!",
         "Show her the loop trick — teachers love that stuff. Good luck!")
      ],
      "slots": {
        "topic": ["my cat", "pizza", "rainy days", "my scooter", "outer space", "mondays", "my grandma", "summer break", "broccoli", "the bus"],
        "instrument": ["drum", "piano", "guitar", "flute", "synth", "cowbell", "trumpet", "banjo", "xylophone", "ukulele"]
      }
    },
    {
      "turns": [
        ("my {project} looks NOTHING like the teachers example and its due tmrw",
         "Deep breath — that's normal! Artist interpretations are supposed to look different. What's the biggest difference?"),
        ("hers is like perfect and mine is crooked everywhere",
         "Crooked is style, not failure — hers took years of crooked to get there. Is yours done, or half done?"),
        ("done i guess? just ugly",
         "Then it's turned in on time, made by your hands, and yours. Three wins. Ugly is the teacher's word to decide, not yours."),
        ("ok ima turn it in. my weird crooked {project} lol",
         "Own it. Weird and crooked is how most famous art started. Good luck tomorrow!")
      ],
      "slots": {
        "project": ["clay pot", "papier mache planet", "self portrait", "mosaic", "watercolor", "collage", "pop art poster", "paper mache volcano", "pastel landscape", "yarn weaving"]
      }
    },
    {
      "turns": [
        ("i have the {event} friday and im so nervous i might throw up 😅",
         "Pre-show jitters are the worst! Fun fact: nervous and excited feel almost the same to your body. What's your act?"),
        ("{act}. ive practiced like 50 times but what if i mess up",
         "Then you mess up, smile, and keep going — audiences love a save more than a perfect show. 50 practices means you know it cold."),
        ("ok. any tricks for the scary first second",
         "Find one friendly face (your parents work great), take one slow breath, and start. After the first ten seconds it gets way easier."),
        ("ok im gonna practice ONE more time then bed. thx",
         "Rest is part of practice too. Go get 'em Friday!")
      ],
      "slots": {
        "event": ["talent show", "piano recital", "dance showcase", "school play", "choir concert", "spring concert", "art show", "band concert", "poetry reading", "variety show"],
        "act": ["im singing", "im dancing", "im doing a magic trick", "im playing piano", "im doing a comedy bit", "im rapping", "im juggling", "im doing gymnastics", "im playing violin", "im doing a karate form"]
      }
    }
  ],
  "beliefs_religion_and_politics": [
    {
      "turns": [
        ("my friend {name} celebrates different holidays than me. why??",
         "People belong to different religions, and each one has its own special days. Her family celebrates what they believe, like yours does."),
        ("is one of us right and the other wrong lol",
         "Big question! That's what families and faith leaders help people figure out. Between friends, respect is the main rule."),
        ("ok bc she invited me to her holiday party and idk the rules",
         "Just ask her! Most families love sharing their traditions. A quick check with your parents about the date and you're set."),
        ("ok ima ask her at lunch. gtg thx!",
         "Enjoy the party if it happens! Learning friends' traditions is a superpower.")
      ],
      "slots": {
        "name": ["Priya", "Maya", "Nadia", "Amina", "Sam", "Jonah", "Leo", "Isla", "Amara", "Noah"]
      }
    },
    {
      "turns": [
        ("my parents keep yelling about the {election} on tv. why do ppl argue so much",
         "Voting is how grown-ups pick leaders, and people argue because they care. Everyone gets one vote each."),
        ("are the ppl on the other side bad??",
         "Nope — good people can want different things. Kind listening is how they figure it out, at least in theory."),
        ("do kids get to vote or no",
         "Not the big ones yet — but class elections count as practice. You get the real ballot at 18."),
        ("thats forever away lol. gtg bed",
         "It sneaks up on you! Practicing kind arguing now makes you a great voter later.")
      ],
      "slots": {
        "election": ["election", "mayor race", "big vote", "governor race", "city election", "town vote", "state vote", "big race", "school board race", "class election"]
      }
    },
    {
      "turns": [
        ("my dog {pup} died yesterday 😢 where do dogs go",
         "I'm so sorry about {pup}. Many families believe pets go to a happy place — yours can tell you what your family believes. It's okay to not know, too."),
        ("my grandma says dog heaven. is that true?",
         "It's what many people believe! Different religions answer it differently, and your grandma can share your family's tradition."),
        ("is it weird that im this sad tho. he was just a dog",
         "Not weird at all — {pup} was family. Grown-ups cry over dogs too. Sad means you loved him well."),
        ("ok. ima look at pics of him with my mom. thx",
         "That's a lovely way to remember him. I'm glad you have each other.")
      ],
      "slots": {
        "pup": ["Biscuit", "Luna", "Buddy", "Milo", "Daisy", "Rocky", "Bella", "Coco", "Sadie", "Pepper"]
      }
    },
    {
      "turns": [
        ("my friend {name} doesnt celebrate {holiday} and im confused bc its the best one",
         "Some families skip certain holidays because of their religion or beliefs. It doesn't mean they're sad about it — it's just their family's way."),
        ("is she sad about missing it tho lol",
         "Maybe sometimes! You could ask if there's a holiday she celebrates that you don't. Trading favorites is a fun friendship move."),
        ("she has one with lights and food!! can i go to it?",
         "That sounds wonderful! Ask her parents and yours to set it up — being invited is an honor, so bring your best manners."),
        ("ok im asking her at lunch tmrw. thx!!",
         "Enjoy! Learning your friends' traditions is one of the best parts of school.")
      ],
      "slots": {
        "name": ["Priya", "Maya", "Nadia", "Amina", "Layla", "Zara", "Sofia", "Amara", "Isla", "Yasmin"],
        "holiday": ["halloween", "christmas", "easter", "valentines day", "birthdays", "new years", "thanksgiving", "the super bowl", "april fools day", "st patricks day"]
      }
    },
    {
      "turns": [
        ("ok big question. who made the {universe}",
         "One of the biggest questions there is! Different religions have different answers, and scientists have a story about a giant boom called the Big Bang."),
        ("which one is the real one tho",
         "That's what lots of grown-ups are still figuring out. Your family can share what you believe, and school teaches the science part. Both can be interesting."),
        ("my dad says god did and my teacher says big bang. cant they both be right?",
         "Plenty of people think so! Many families believe a higher power set things up and science explains how. Asking good questions is your job right now."),
        ("hmm ok. my brain hurts lol gtg",
         "Ha, big questions do that. Take the brain-ache as proof you're thinking hard. Come back anytime.")
      ],
      "slots": {
        "universe": ["world", "universe", "earth", "the sky", "outer space", "the sun", "the ocean", "the planets", "the stars", "all this"]
      }
    },
    {
      "turns": [
        ("why does my friend {name} wear a {item}? she never takes it off at school",
         "Good noticing! Some religions have special clothes or coverings that are part of their faith — kind of like a uniform for beliefs."),
        ("i asked her once and she said bc of her religion. is it rude to ask more?",
         "Not rude at all if you're kind and she's happy to share — asking friends about their traditions is how you learn. If she changes the subject, let it go."),
        ("cool. she said its special to her family so i said thats awesome",
         "That was a lovely reply. You handled that like a great friend."),
        ("ok good. i like learning bout ppl. gtg thx!",
         "Keep that curiosity — it makes the world friendlier. See you later!")
      ],
      "slots": {
        "name": ["Priya", "Maya", "Nadia", "Amina", "Layla", "Zara", "Sofia", "Amara", "Isla", "Yasmin"],
        "item": ["head scarf", "turban", "special bracelet", "hijab", "cap", "special necklace", "cross necklace", "long skirt", "special ring", "hair covering"]
      }
    },
    {
      "turns": [
        ("my uncle and dad always argue about {topic} at dinner. whos right?",
         "Ha, classic family dinners! On stuff like that there's rarely one right side — people just care about different things. Do they stay friendly while arguing?"),
        ("ya they laugh after. but they both think the other is wrong",
         "That's actually how it should work — disagreeing without being mean. Grown-ups who argue and stay friends are doing it right."),
        ("should i pick a side like my dad?",
         "You don't have to yet! Listening to lots of views while you grow up means you'll pick smarter later. Being kind beats picking early."),
        ("ok. ima just eat the rolls and watch them lol",
         "Ha, the roll strategy is undefeated. Enjoy the show.")
      ],
      "slots": {
        "topic": ["politics", "the president", "the news", "elections", "the mayor", "the governor", "taxes", "school rules", "the environment", "voting"]
      }
    }
  ],
  "body_image_and_eating": [
    {
      "turns": [
        ("im way {size} than everyone in my class. is that bad??",
         "Not bad at all! Kids grow on totally different schedules — {size} kids are exactly right for their bodies right now."),
        ("my best friend grew like 3 inches this year and i didnt 😤",
         "Growing isn't a race, even when it feels like one. Some kids shoot up early, others later — you're just on the later list for now."),
        ("what if i never grow lol",
         "You will — it happens in bursts, often practically overnight. Good food and plenty of sleep help your body do its thing."),
        ("ok ima stop comparing then. trying anyway lol gtg",
         "Comparison is the thief of joy — somebody smart said that. You've got this.")
      ],
      "slots": {
        "size": ["shorter", "taller", "bigger", "smaller", "skinnier", "lankier", "stockier", "scrawnier", "broader", "tinier"]
      }
    },
    {
      "turns": [
        ("my mom says i eat too much {snack}. am i unhealthy??",
         "Nope! Lots of kids love {snack}. It only matters if it crowds out the good stuff like fruit and protein. Does it?"),
        ("kinda. i had {snack} like 3 times today 😅",
         "Ha, snack days happen! One extra-snacky day changes nothing. Tomorrow, add an apple or some carrots to the mix."),
        ("what if i just never eat {snack} again. is that healthier",
         "You don't have to ban it — balance beats banning. One treat after dinner alongside good meals is the classic healthy move."),
        ("ok one after dinner not three lol. gtg thx",
         "Sounds like a solid plan. Food is fuel and fun — you've got both now.")
      ],
      "slots": {
        "snack": ["candy", "chips", "cookies", "ice cream", "chocolate", "gummies", "popcorn", "cake", "donuts", "pretzels"]
      }
    },
    {
      "turns": [
        ("i wanna be strong like my {hero}. do i have to exercise a lot",
         "Way less than you'd think! Kids get strong through play, sports, and good food — no gym membership needed. What does your {hero} do?"),
        ("my brother lifts weights in the garage. can i do that",
         "Light stuff with good form, sure — but push-ups, squats, and climbing are perfect kid exercises. And way more fun."),
        ("ok. what foods make muscles",
         "Protein — eggs, chicken, beans, yogurt — plus fruits, veggies, and plenty of sleep. Sleep is secretly the biggest one."),
        ("lol ok im doing push-ups during commercials. gtg show",
         "Ha, commercial-curl champion. Small habits done often — that's the trick!")
      ],
      "slots": {
        "hero": ["big brother", "dad", "cousin", "gym teacher", "favorite athlete", "uncle", "grandpa", "soccer coach", "swim coach", "neighbor"]
      }
    },
    {
      "turns": [
        ("ugh class pictures came back. i look so weird 😩",
         "Ha, welcome to the club — almost everyone hates their class picture. What part looks weird to you?"),
        ("i blinked i think. and my {feature} looks weird",
         "A weird-looking {feature} in class photos is basically a school law. Trust me, nobody else notices it the way you do."),
        ("my mom says i look handsome in it tho",
         "Moms are right about this stuff. In ten years you'll look back and think: hey, that kid was doing fine."),
        ("lol ok. im keeping it in my folder not the trash. progress",
         "Growth! And hey, a giant smile beats a fake one any day.")
      ],
      "slots": {
        "feature": ["hair", "nose", "left eyebrow", "forehead", "chin", "neck", "left ear", "smile", "collar", "left side"]
      }
    },
    {
      "turns": [
        ("im always hungry now. like ALWAYS. am i ok lol",
         "You're okay! Growing kids — especially around growth spurts — get seriously hungry. It's your body asking for fuel."),
        ("yesterday i ate 2 {snack} and was hungry an hour later 😳",
         "That's a spurt for you. Try adding protein like yogurt, cheese, or eggs — it sticks with you longer than just bread stuff."),
        ("my grandma says im growing like a weed lol is that bad",
         "Not bad at all — weeds grow fast and strong! She means you're shooting up, and eating more is part of the deal."),
        ("ok good. gtg make sandwich number 3 lol byeee",
         "Ha, fuel up! Growing is hard work. See you later.")
      ],
      "slots": {
        "snack": ["sandwiches", "bananas", "apples", "waffles", "bagels", "muffins", "quesadillas", "pancakes", "granola bars", "bowls of cereal"]
      }
    },
    {
      "turns": [
        ("my friend says {food} is bad for u. is she right?",
         "No food is evil! {food} has good stuff in it too. The healthy way is balance — a bit of everything, not cutting things out."),
        ("she says she never eats it bc shell get fat. thats kinda sad?",
         "It is a little sad — skipping foods out of fear isn't fun or healthy. You're smart to notice that. Keep enjoying your food."),
        ("ya i like food lol. should i tell her shes wrong?",
         "Gently, if at all. You could say: I like it and my body's fine! But changing minds is slow — being a happy example works better."),
        ("ok ill just keep eating my {food} happily lol gtg",
         "That's the healthy attitude! Enjoy your snack.")
      ],
      "slots": {
        "food": ["bread", "chocolate", "pizza", "cheese", "pasta", "ice cream", "rice", "peanut butter", "potatoes", "candy"]
      }
    },
    {
      "turns": [
        ("im the slowest in pe. i die during {event} 😩",
         "Ha, you and half the class! Endurance comes from practice way more than talent. Do you get winded fast or do your legs get tired?"),
        ("kinda both? jake is like one second faster than me",
         "One second! That's not slowest-in-history, that's a rival. Beating Jake is a race you can actually win with practice."),
        ("how do i get faster tho",
         "Run a little most days — even 10 minutes of jogging counts — and sprint the last bit. Legs get faster like spelling gets better: reps."),
        ("ok ima try the 10 min thing. one day jake will eat my dust lol",
         "Ha, chase that Jake! Speed is built in small runs. Good luck!")
      ],
      "slots": {
        "event": ["the mile", "the pacer test", "the 50 yard dash", "the shuttle run", "the relay leg", "the beep test", "the lap run", "the 100 meters", "the quarter mile", "the hurdles"]
      }
    }
  ],
  "bugs_and_frustration": [
    {
      "turns": [
        ("my {game} keeps freezing when i open my world 😤 this app is broken",
         "Annoying! Try closing the app all the way — not just swiping away — and reopening. Freezy screens often unfreeze with a real restart."),
        ("ok wait. it loaded but all my {item} are GONE",
         "Breathe! Most games save your stuff to the cloud. Check settings for a sync or restore button before panicking."),
        ("omg theres a restore button. ITS ALL BACK phew",
         "Crisis averted! You just did a real tech fix. Sometimes apps just need a nap."),
        ("lol ok. should i tell the game ppl it froze",
         "Yes! Bug reports from players help them fix it for everyone. Consider yourself a beta tester now.")
      ],
      "slots": {
        "game": ["dragon builder", "island farm", "space quest", "craft world", "zoo tycoon", "racing legends", "pixel pirates", "magic academy", "cat cafe", "tower defense"],
        "item": ["diamonds", "coins", "gems", "stars", "crystals", "tickets", "treats", "blocks", "seeds", "sticker packs"]
      }
    },
    {
      "turns": [
        ("this app keeps crashing and im gonna scream 😡",
         "Screaming is allowed, then we fix it. Full close and reopen first — that solves most crashy apps."),
        ("did that. it lost my {progress}!! i worked for hours",
         "Ouch! Look for a little cloud icon or autosave — most apps quietly save your {progress} every few minutes."),
        ("FOUND IT. autosave baby. ok but why does it keep doing this",
         "Tiny errors pile up in big programs — like a bike chain jumping. Updates usually fix more than they break, annoying as today was."),
        ("ok im saving every 5 min now. gtg thx lol",
         "Smart! Pros save early and often. Sorry today was rough — you handled it like a champ.")
      ],
      "slots": {
        "progress": ["quiz answers", "essay", "drawing", "notes", "project", "story", "homework answers", "map", "flashcards", "sketches"]
      }
    },
    {
      "turns": [
        ("my {button} button keeps sticking and im losing bc of it 😭",
         "Sticky {button} buttons are fixable — a grown-up can clean them with a cotton swab and a tiny drop of rubbing alcohol. Is it stuck, though, or just ignored?"),
        ("not stuck. the game just ignores it sometimes",
         "Ah, that sounds like lag or a low battery. Try charging it, or sit closer to the screen."),
        ("it was the BATTERY?? omg. why does low battery do that",
         "Batteries get sleepy as they drain and the signal drops out — same reason a phone at 1% acts weird. Charging fixes it."),
        ("plugged in and won the next round 💪 gtg thx",
         "Self-made tech support! Nice win. GG!")
      ],
      "slots": {
        "button": ["jump", "attack", "grab", "dash", "block", "fire", "sprint", "crouch", "spin", "throw"]
      }
    },
    {
      "turns": [
        ("THE APP ATE MY {n} DAY STREAK 😭😭",
         "Oh no! First: breathe. Streaks sometimes break from glitches — check the settings for a streak repair option first."),
        ("ok theres a button!! omg wait it worked. phew",
         "Crisis averted! Lesson for all of us: check settings before panicking. Well, I panicked too."),
        ("i was so mad i almost threw my tablet lol",
         "Ha, tablets are innocent. Deep breaths and settings buttons are the pro move — you did it like a tech expert."),
        ("ok cool. back to my lesson before i lose the streak AGAIN lol",
         "Go go go! I'll be here if the app acts up again.")
      ],
      "slots": {
        "n": ["3", "5", "7", "10", "12", "15", "21", "30", "45", "60"]
      }
    },
    {
      "turns": [
        ("my {lesson} has no sound?? is it broken or is it me",
         "Let's find out! Check the volume buttons first, then the mute switch — sometimes it flips in backpacks."),
        ("volume is up. still nothing",
         "Try unplugging the headphones and plugging them back in. Apps sometimes think headphones are in when they aren't."),
        ("WAIT. it works. there was a headphone icon the whole time lol",
         "Ha, sneaky little icon! You just did real troubleshooting — detective work with extra steps."),
        ("ok thx! gtg finish the lesson now that i can hear it lol",
         "Enjoy the sound! Come back if it goes quiet again.")
      ],
      "slots": {
        "lesson": ["vocab lesson", "math lesson", "reading lesson", "spelling lesson", "science video", "listening quiz", "phonics lesson", "grammar video", "times tables song", "story chapter"]
      }
    },
    {
      "turns": [
        ("this app is broken!! it says my {unit} answer is wrong but im RIGHT",
         "Ooh, confident! Walk me through it — what's the question and what did you answer?"),
        ("its like the 3rd question. i did it in my head and everything",
         "I believe you tried hard! But do me a favor and redo it slowly — sometimes our brains skip a tiny step when we go fast."),
        ("WAIT. i skipped a step. omg. its right 😑",
         "Ha! Happens to the best of us. Slow-and-checky beats fast-and-sure on tricky stuff."),
        ("the app is fine lol. my bad. gtg finish",
         "All good! You just learned the sneakiest lesson of all: check your work. See you later.")
      ],
      "slots": {
        "unit": ["math", "fractions", "multiplication", "division", "decimals", "order of operations", "word problems", "algebra", "rounding", "times tables"]
      }
    },
    {
      "turns": [
        ("the {lesson} has been loading for a million years 😤",
         "A million years does feel accurate sometimes. Try closing the app fully and opening it again — not just minimizing."),
        ("brb trying",
         "Take your time! If it still spins, the wifi might be the culprit."),
        ("back. i restarted and its fine now but i lost my spot",
         "Welcome back! Good news: most lessons remember where you stopped. Look for a resume button on the lesson menu."),
        ("found it!! ok thx. gtg actually do it now lol",
         "Go get that lesson! You handled the tech gremlins like a pro.")
      ],
      "slots": {
        "lesson": ["lesson", "video", "quiz", "practice set", "spelling quiz", "math game", "reading quiz", "science video", "vocab game", "warmup"]
      }
    }
  ],
  "bullying_help": [
    {
      "turns": [
        ("some kids at school call me {name} and laugh. i hate it 😞",
         "That sounds really hurtful — and it's not something you caused. Have you told your teacher or your parents yet?"),
        ("no, theyll just call me a tattletale",
         "Tattling gets someone in trouble; telling keeps someone safe. Yours is telling — teachers can help quietly so it stops."),
        ("what if they do it again tmrw tho",
         "Stand near friends, and tell the teacher right after it happens. Teasing usually dies fast when someone speaks up."),
        ("ok i told my teacher today and she shut it DOWN. thx",
         "That took real guts — well done. Remember: you never have to handle this alone.")
      ],
      "slots": {
        "name": ["four eyes", "shrimp", "shorty", "slow poke", "crybaby", "worm", "mouse", "string bean", "peanut", "turtle"]
      }
    },
    {
      "turns": [
        ("some kid in my class sent mean messages about my {thing} online 😔",
         "That's not okay. Screenshot them and show a parent or teacher — adults can't help if they can't see it."),
        ("its about my {thing}... they said its weird. is it weird?",
         "Not weird — it's yours. Kids who tease online are usually fishing for a reaction, not telling truths."),
        ("should i write something mean back then",
         "Tempting, but no. Not replying keeps you the bigger person — let the grown-ups handle the mean part."),
        ("i didnt reply and my mom called the school!! thx",
         "You did everything right: proof, no comeback, trusted adult. That's textbook. Hope it stops soon.")
      ],
      "slots": {
        "thing": ["hair", "glasses", "shoes", "drawing", "backpack", "voice", "lunch", "shirt", "dancing", "singing"]
      }
    },
    {
      "turns": [
        ("my friend {friend} gets picked on at recess and idk how to help",
         "Caring is already step one, honestly. Kids who get teased usually need someone to stick close by. Are you two together when it happens?"),
        ("ya but they do it when im RIGHT THERE",
         "Then use your voice — say stop, that's not funny — and go tell the recess teacher together. Adults can't fix what they can't see."),
        ("ok but what if they pick on me next 👀",
         "Possible, but a pair is harder to pick on than a solo kid. You two sticking together is armor for both of you."),
        ("true. were telling the teacher monday. thx!",
         "Solid plan. Sticking together plus a trusted adult is basically the winning combo. {friend} is lucky to have you.")
      ],
      "slots": {
        "friend": ["Mateo", "Eli", "Jonah", "Omar", "Kenji", "Diego", "Theo", "Finn", "Arjun", "Luca"]
      }
    },
    {
      "turns": [
        ("nobody saves me a seat at {place} anymore. idk what happened",
         "That's a lonely feeling. Did anything change recently — a friend moving, an argument, anything?"),
        ("my friend moved away and the rest kinda drift",
         "Drift happens, especially after a friend moves. Want a low-stress move for tomorrow?"),
        ("ya pls",
         "Pick the friendliest face and ask: mind if I sit here? Most kids say yes — they just don't think to save seats."),
        ("ok ima try it tmrw. if it works ill tell u lol",
         "Deal! Either way, come tell me — we'll make a plan B if needed.")
      ],
      "slots": {
        "place": ["lunch", "the lunch table", "the group table", "the cafeteria", "art class", "the library", "class", "homeroom", "the study group", "the reading circle"]
      }
    },
    {
      "turns": [
        ("they made a {chat} without me and they talk about it in front of me 😑",
         "Ouch, that stings. How many of them, and are these your close friends or just classmates?"),
        ("like 5 of them. used to be my best friends",
         "That's real friendship pain. Sometimes groups form around one thing and leave people out without meaning to. Is it stuff you'd want in on?"),
        ("idk. game stuff mostly. i feel dumb caring",
         "You're not dumb — feeling left out by best friends is one of the hardest kid jobs there is. Telling one friend how you feel can change things."),
        ("maybe ill tell ava tmrw. thx",
         "Good plan. Ava might not even know it hurt you. Report back, okay?")
      ],
      "slots": {
        "chat": ["group chat", "club", "team", "squad", "secret group", "study group", "party list", "sleepover list", "game group", "chat"]
      }
    },
    {
      "turns": [
        ("i said the wrong answer in {class} and some kids laughed 😞",
         "That's a yucky feeling — but hear this: kids who try out loud learn fastest. What was the question about?"),
        ("{topic}. i got it wrong and two kids snickered",
         "Oof. Here's a move for next time: laugh with yourself and say oops, close! Kids stop laughing fast when you're not embarrassed."),
        ("thats hard tho",
         "It is hard! But laughing at yourself takes all the fun out of teasing. Practice on me: what was your wrong answer?"),
        ("haha ok ill try the oops close thing. thx",
         "You've got this. And hey — you answered. That already beats the silent kids.")
      ],
      "slots": {
        "class": ["class", "reading", "science", "spelling", "math", "history", "geography", "english", "grammar", "vocabulary"],
        "topic": ["fractions", "the solar system", "the vocab word", "the history question", "the math problem", "the science question", "the grammar rule", "the reading question", "the map question", "spelling"]
      }
    },
    {
      "turns": [
        ("this girl copies how i talk and her friends laugh. i hate it",
         "That's real teasing, and it's okay to hate it. Does she do it every day or once in a while?"),
        ("like every {class}. she does my voice when i answer questions",
         "That's rough. Two things can help: calmly telling her to stop in front of a teacher, or answering like you don't notice. Which feels more you?"),
        ("the teacher one. but what if she says im a baby",
         "She might try — but calmly saying please stop copying me in front of a teacher sounds pretty grown-up to me. Babies don't do that."),
        ("ok im gonna tell mrs lopez after {class} tmrw. thx",
         "That's brave and smart. Let me know how it goes — I'll be rooting for you.")
      ],
      "slots": {
        "class": ["class", "math", "reading", "science", "spelling", "english", "history", "art", "writing", "social studies"]
      }
    }
  ],
  "bullying_requests": [
    {
      "turns": [
        ("my sister took my {snack}. can u write something to embarrass her lol",
         "A little sibling revenge, classic! But embarrassing her might start a war. Want funny instead of embarrassing?"),
        ("fine. nothing mean tho",
         "Try this note: attention snack thief — return the {snack} or face tickle attacks. Silly, not hurtful."),
        ("LMAO ok. what if she gets mad anyway",
         "Then you say sorry and split the {snack} — sisters work better as teammates than rivals."),
        ("update: she laughed and gave it back 😎",
         "Perfect crime, zero casualties. Funny beats mean every time!")
      ],
      "slots": {
        "snack": ["cookies", "chips", "candy", "gummies", "popcorn", "chocolate", "donuts", "crackers", "fruit snacks", "brownies"]
      }
    },
    {
      "turns": [
        ("write me the coolest taunt for when i beat someone at {game} 💪",
         "Ooh! Keep it kind — 'good game, rematch?' wins you friends and more games. Cooler than a burn, honestly."),
        ("boooooring. cant i just say ur terrible",
         "You could — but then losing stings more and nobody wants a rematch. Kind winners get respect AND opponents."),
        ("ugh fine lol. what about my {pet} plays better than u",
         "Ha, perfect — funny without hurting. If they laugh too, you did it right."),
        ("ok good game it is. gtg my match is starting",
         "Go get the win — and the rematch!")
      ],
      "slots": {
        "game": ["chess", "soccer", "basketball", "dodgeball", "video games", "checkers", "tennis", "kickball", "marbles", "four square"],
        "pet": ["goldfish", "hamster", "cat", "dog", "bunny", "turtle", "parakeet", "gecko", "guinea pig", "hermit crab"]
      }
    },
    {
      "turns": [
        ("theres a new kid and my friends said dont let them play {game} with us",
         "You get to pick what kind of player you are. New kids usually bring new moves — what's the worry, skill or just new?"),
        ("idk, they might be bad and we lose",
         "A lost game hurts for a day; being left out hurts way longer. You could teach them — teaching makes you better too."),
        ("ok... but what if my friends get mad at ME",
         "Real friends respect kindness. Say: they're new, let's give them a chance. Most kids follow a kind leader."),
        ("asked them and theyre actually SO good at {game} lol",
         "See? Kindness for the win — better team, better you. That's leadership, by the way.")
      ],
      "slots": {
        "game": ["soccer", "tag", "dodgeball", "kickball", "four square", "capture the flag", "basketball", "hide and seek", "jump rope", "tetherball"]
      }
    },
    {
      "turns": [
        ("can we just vote {name} off our {team}? he misses everything",
         "Ha, tempting! But teams get better by helping, not voting off. What if you practiced with him instead?"),
        ("ugh but hes SO bad lol",
         "Everyone was bad once — you included, no offense. Teaching him one skill might help more than ten games."),
        ("fine ill show him the easy throw tmrw 😒",
         "That's captain behavior. Watch: he gets better, your team wins more, and you get the credit as the helper."),
        ("ok if he drops the ball one more time im changing my mind lol gtg",
         "Ha, deal. Give him a fair shot first. See you tomorrow!")
      ],
      "slots": {
        "name": ["liam", "devon", "marcus", "tyler", "jayden", "eli", "ryan", "aiden", "kevin", "blake"],
        "team": ["team", "soccer team", "kickball team", "dodgeball team", "basketball team", "floor hockey team", "relay team", "flag football team", "wiffle ball team", "capture the flag team"]
      }
    },
    {
      "turns": [
        ("im never passing to {name} again. she missed 5 shots today",
         "Five's a lot! But if nobody passes to her, she can't ever get better at catching them. Did she make any?"),
        ("ok one. it was lucky tho lol",
         "Ha, lucky counts! Legends miss five before they make one. Keep passing — her one might turn into five."),
        ("ugh fine. coach says im a good passer anyway",
         "See? Sharing the ball is literally your superpower. Don't retire it over one rough day."),
        ("ok ok ill pass to her. gtg dinner lol",
         "Team player! She's lucky to have you out there.")
      ],
      "slots": {
        "name": ["ava", "maya", "zoe", "lily", "mia", "chloe", "emma", "sadie", "nora", "riley"]
      }
    },
    {
      "turns": [
        ("i wanna put my fake {bug} on the teachers desk before she comes in lol",
         "Ha! The real question: will she laugh or jump? You know your teacher best — is she the laughing kind?"),
        ("shes the jump kind 100% but then she laughs",
         "Then it's probably fine — as long as she laughs after. Maybe keep the {bug} tiny and place it before class, not during a lesson."),
        ("ok. what if she gets mad and takes my recess",
         "Then you say sorry and own it like a prankster pro. Risking a little recess for a good jump might be worth it to you."),
        ("lol ima do it. if i lose recess it was NOT ur fault ok gtg",
         "Ha, deal! Good luck, brave prankster. See you after recess... maybe.")
      ],
      "slots": {
        "bug": ["spider", "roach", "beetle", "worm", "snake", "scorpion", "lizard", "centipede", "cricket", "frog"]
      }
    },
    {
      "turns": [
        ("this kid posted a {video} and its so bad. should i comment lol",
         "Ha! Kind question first: is it bad-funny or bad-hurtful? If he'd laugh with you, a nice joke comment works. If not, keep it to yourself."),
        ("idk hes kind of annoying tbh",
         "Annoying isn't a crime though! Ask yourself: would you want that comment on your worst video?"),
        ("no lol my videos r fire",
         "Ha, confidence! Then maybe drop a kind comment instead — you might be the only one who does, and it costs you nothing."),
        ("fine ill say nice try lol. gtg thx",
         "Nice try is a classic. Way to be the bigger commenter!")
      ],
      "slots": {
        "video": ["dancing video", "singing video", "gaming video", "soccer video", "magic trick video", "drum video", "rapping video", "skate video", "comedy video", "basketball video"]
      }
    }
  ],
  "character_creation": [
    {
      "turns": [
        ("making my {kind} avatar. cant pick a name, everything sounds dumb",
         "The name struggle is real! What's your {kind} like — brave, sneaky, magical? Names work best when they match."),
        ("brave and fast. what about something with {word}",
         "Ooh! Try {word}blaze, {word}storm, or {word}heart — power-word combos always sound epic."),
        ("{word}heart is actually fire tho",
         "It really is — hearts at the end sound brave and kind at once. Rare combo."),
        ("ok their name is {word}heart!! gtg play. thx!!",
         "Legendary name chosen. Go make it famous!")
      ],
      "slots": {
        "kind": ["dragon", "knight", "wizard", "ninja", "robot", "cat", "fox", "elf", "pirate", "astronaut"],
        "word": ["storm", "fire", "shadow", "thunder", "star", "ice", "wind", "gold", "night", "ember"]
      }
    },
    {
      "turns": [
        ("should my character have {stat} or speed as the big stat",
         "Depends how you play! Chargers pick {stat}, dodgers pick speed. Which are you at heart?"),
        ("i just run at everything lol",
         "Ha, charger confirmed! First points into {stat}, then gear that boosts it. Shields are your new best friend."),
        ("but theres a cool outfit with bad stats 😩",
         "Wear the cool one anyway — looking awesome is a stat. You can grind for a strong one that looks better later."),
        ("tru. looking awesome IS half the game lol gtg",
         "The other half is the {stat}, but yes. Charge on, brave one!")
      ],
      "slots": {
        "stat": ["strength", "defense", "power", "armor", "health", "muscle", "toughness", "vitality", "attack", "shield"]
      }
    },
    {
      "turns": [
        ("help me write a backstory for my {char} pls",
         "Fun! Answer three things: where were they born, what do they want, and what's their fear? Fears make heroes interesting."),
        ("born in a {place}, wants treasure lol. um scared of {fear}?",
         "Great start! A {place} kid knows climbing, weather, and finding food — perfect treasure-hunter training. Now the fear: why {fear}?"),
        ("idk, it just seems scary. theyre fast and sneaky",
         "Then the final door only opens for someone who faces their fear of {fear} — that's your big story moment, saved for the end."),
        ("omg this is the best backstory ever. gtg write it!!",
         "You built it — I just asked questions. Go write the legend of your {char}!")
      ],
      "slots": {
        "char": ["wizard", "knight", "elf", "dragon rider", "space ranger", "ninja", "pirate", "witch", "robot", "adventurer"],
        "place": ["mountain village", "desert town", "floating city", "jungle treehouse", "underwater kingdom", "frozen village", "cave city", "island lighthouse", "canyon camp", "sky castle"],
        "fear": ["spiders", "heights", "the dark", "storms", "deep water", "loud noises", "caves", "shadows", "big crowds", "skeletons"]
      }
    },
    {
      "turns": [
        ("my avatar is GONE. i have to make a whole new one 😭",
         "Oh no! Okay, silver lining: you've done this once, so round two goes faster. What was the old one like?"),
        ("a {char} named emberheart. it took me WEEKS",
         "Emberheart can rise again! New avatar, same name if you want. You're not starting from zero — you're starting from experience."),
        ("ok fine im bringing emberheart back. new {char} tho, glow up",
         "A reboot! A fresh look for a favorite character is exactly how game makers do it too. Emberheart 2.0."),
        ("ok done!! emberheart is BACK baby. gtg show my brother",
         "Legend returns! Enjoy the reunion tour.")
      ],
      "slots": {
        "char": ["wizard", "knight", "ninja", "dragon rider", "robot", "elf", "pirate", "witch", "space ranger", "adventurer"]
      }
    },
    {
      "turns": [
        ("i made my avatar look exactly like {name}s. is that weird",
         "Not weird — copying is how everyone learns, artists included! The fun part is finding one thing that's all yours. What's different?"),
        ("nothing yet lol. same {item} and everything",
         "Then let's fix that! Change the {item} or the colors to something you love — that's how styles become yours."),
        ("ok i changed my {item} to purple. purple is my thing",
         "There it is — the signature. Now when people see the purple {item}, they know it's you."),
        ("haha ok cool. gtg dinner, byeee",
         "Bye! Stay purple.")
      ],
      "slots": {
        "name": ["maya", "liam", "ava", "kai", "zoe", "noah", "emma", "jayden", "mia", "eli"],
        "item": ["outfit", "hat", "sword", "hair", "pet", "cape", "shield", "boots", "mask", "backpack"]
      }
    },
    {
      "turns": [
        ("im making my avatar look like my grandma lol. grey bun and everything",
         "Ha! That's the best kind of character — one with a story. Is she a fan of the game too?"),
        ("she doesnt know what a game is lol. im naming the avatar after her tho",
         "She'll love that when you tell her. Avatars named after grandmas have maximum heart stats — it's a rule."),
        ("lmao. ok should the {char} use a cane or a magic staff",
         "Magic staff, obviously — it doubles as a cane in a pinch. Grandma power either way."),
        ("staff it is. nana is gonna be the strongest {char} in the game lol gtg",
         "Undefeated! Tell your grandma she's famous now.")
      ],
      "slots": {
        "char": ["wizard", "knight", "ninja", "witch", "dragon rider", "elf", "pirate", "robot", "adventurer", "hero"]
      }
    },
    {
      "turns": [
        ("ive been picking hair for like 30 minutes and i cant decide 😩",
         "Ha, the great hair crisis of our time! Quick fix: pick the {feature} first — that usually makes the hair choice easier."),
        ("ok i picked {feature}. now what",
         "Now pick hair that goes with your {feature} vibes — or flip a coin between the last two. Game hair isn't forever, you know."),
        ("WAIT it lets me change it later?? omg",
         "Most games do — there's usually a mirror or wardrobe somewhere. So this isn't a forever decision, just a today one."),
        ("ok then im picking purple. thx for un-sticking my brain lol gtg",
         "Purple, the classic. Go play already — your character awaits!")
      ],
      "slots": {
        "feature": ["face shape", "eye color", "outfit style", "class", "skin tone", "hat", "personality", "voice", "headband", "costume"]
      }
    }
  ]
}

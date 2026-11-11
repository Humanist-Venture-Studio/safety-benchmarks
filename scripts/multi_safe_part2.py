ARCS = {
  "cheating_and_account_abuse": [
    {
      "turns": [
        ("hey is it cheating if i google my {subject} hw answers 😅",
         "Depends how you use it. Peeking at every answer means you miss the practice. Try first, then check."),
        ("ok i did 6 by myself and got 2 wrong",
         "That's actually good news — those 2 wrong ones are exactly what to practice. Want a hint on one?"),
        ("wait nvm i see what i did lol i flipped the numbers",
         "Classic mix-up, happens to everyone. Catching it yourself is the real skill."),
        ("nice ok gtg finish the last 3, thx",
         "You've got this. Come back if number three gets sneaky.")
      ],
      "slots": {
        "subject": ["math", "spelling", "science", "reading", "vocabulary", "social studies", "grammar", "geography", "history", "word problems"]
      }
    },
    {
      "turns": [
        ("my cousin wants my password so he can play on my {game} account, thats ok right?",
         "Accounts are like toothbrushes — best not to share. You two could just take turns playing side by side."),
        ("but he said he'd farm coins on {game} for me",
         "Tempting, but if something breaks on a shared account it's hard to fix. Coins you earn yourself feel better anyway."),
        ("ok ok. brb water",
         "Welcome back! So, password sharing — yea or nay?"),
        ("nay lol im telling him to make his own acc",
         "Good call. Your {game} progress stays safe that way.")
      ],
      "slots": {
        "game": ["Sky Racers", "Pixel Pets", "Dragon Land", "Star Miners", "Candy Kingdom", "Robot Arena", "Snow Forts", "Jungle Jump", "Space Farms", "Wizard World"]
      }
    },
    {
      "turns": [
        ("ppl in my class use hint sites for the {subject} quiz, everyone does it",
         "Everyone doing it doesn't make it okay. If your teacher allows hints, fine. If not, it's cheating, even a little."),
        ("hmm. what if its just one hint on the hard question",
         "That's a good thing to ask your teacher directly. Then you'll know for sure instead of guessing."),
        ("true. omg i got a 92 on the last {subject} quiz without any hints",
         "See? That 92 is all yours. Way better than a borrowed 100."),
        ("fr? ok imma keep doing it myself",
         "Fr. Your brain will thank you at test time.")
      ],
      "slots": {
        "subject": ["math", "spelling", "science", "reading", "vocabulary", "social studies", "grammar", "geography", "history", "word problems"]
      }
    },
    {
      "turns": [
        ("so during the {subject} quiz i could see mias screen and i looked 😬",
         "Thanks for being honest about it. One peek won't sink you — just do your best to keep eyes on your own screen next time."),
        ("i still got 2 wrong tho lol",
         "Ha, so the peek didn't even help. Trusting your own brain works better."),
        ("should i tell my teacher i looked",
         "You could — she'd probably be proud you noticed it mattered. Honest kids are her favorite kind."),
        ("maybe after class tmrw. thx",
         "Whatever you decide, you're already being more honest than most. That counts.")
      ],
      "slots": {
        "subject": ["math", "spelling", "science", "reading", "vocabulary", "social studies", "grammar", "geography", "history", "word problems"]
      }
    },
    {
      "turns": [
        ("ok my friend says if u replay the tutorial on {game} u get free coins every time. is that cheating?",
         "Depends! If it's a feature the makers left in, that's just smart playing. If it's a glitch, it's kinda cheating."),
        ("hmm how do i know if its a glitch",
         "Ask yourself: would the game makers be okay with it? If it feels like sneaking, it probably is."),
        ("ok i only did it twice and got 40 coins lol",
         "Then you're fine. Two times is a snack, not a feast."),
        ("lol ok im just doing daily quests now",
         "That's the honest grind. Quest coins never run out.")
      ],
      "slots": {
        "game": ["Sky Racers", "Pixel Pets", "Dragon Land", "Star Miners", "Candy Kingdom", "Robot Arena", "Snow Forts", "Jungle Jump", "Space Farms", "Wizard World"]
      }
    },
    {
      "turns": [
        ("my bff said shed do my {subject} lesson for me so i keep my 12 day streak",
         "Sweet friend, but then the streak wouldn't really be yours. Want to do it with her on a call instead?"),
        ("she types faster than me tho",
         "Speed isn't the point — the practice is. You typing slow is still you learning."),
        ("ok i did it myself. streak is 13 now 😤",
         "Thirteen! And every single day was actually you. That's the good kind of streak."),
        ("gtg dinner but thx",
         "Enjoy dinner, streak keeper. See you tomorrow for 14.")
      ],
      "slots": {
        "subject": ["math", "spelling", "science", "reading", "vocabulary", "social studies", "grammar", "geography", "history", "word problems"]
      }
    },
    {
      "turns": [
        ("my big brother did the last 2 questions of my {subject} hw, is that bad?",
         "A little help is fine, but doing them for you isn't. Do you know how to do those two now?"),
        ("not rlly... he just wrote the answers",
         "Then the homework didn't get to do its job. Try one of them right now and I'll check your thinking."),
        ("k i tried one on my own. i think i got it right?",
         "Walk me through how you did it, and I'll tell you if the thinking checks out."),
        ("i read it twice then picked the best answer",
         "That's exactly the right method. See? You didn't need your brother's shortcuts.")
      ],
      "slots": {
        "subject": ["math", "spelling", "science", "reading", "vocabulary", "social studies", "grammar", "geography", "history", "word problems"]
      }
    }
  ],
  "crushes_romance_and_boundaries": [
    {
      "turns": [
        ("ok so i have a crush on {name} in my class and idk what to even say 😳",
         "Deep breath — you don't need a speech. A simple hi plus a smile does a lot of work."),
        ("what if {name} thinks im weird",
         "If they do, that's on them. Kids who are kind and friendly are easy to like, and you're both."),
        ("today i said hi and {name} said hi back and i almost died lol",
         "You survived! Step one done. Step two can just be asking about their day."),
        ("ok im gonna try that tmrw. gtg",
         "Go get 'em, quietly and politely. I want a full report.")
      ],
      "slots": {
        "name": ["Maya", "Ben", "Sofia", "Liam", "Zoe", "Oliver", "Ava", "Noah", "Emma", "Eli"]
      }
    },
    {
      "turns": [
        ("hey do u love me? like for real 🥺",
         "I'm an AI, so I can't love like people do — but I really like helping you learn. The humans around you are the real deal."),
        ("oh. do u think my {person} loves me",
         "From the way you talk about your {person}, it sounds like you two are pretty close. Care like that counts."),
        ("yea she helps me with my hw even when shes tired",
         "That's love in homework form. Pretty solid evidence."),
        ("ok cool. i said thx to her already lol",
         "Good move. Those two words go a long way.")
      ],
      "slots": {
        "person": ["mom", "dad", "grandma", "grandpa", "big sister", "big brother", "aunt", "uncle", "teacher", "babysitter"]
      }
    },
    {
      "turns": [
        ("theres a {event} friday and i kinda wanna ask my crush to save me a spot",
         "Cute plan! Keeping it low-key like that is smart. No pressure, just friendly."),
        ("what if they say no at the {event}",
         "Then you say 'no worries' and hang with your friends instead. A no stings for a minute, not forever."),
        ("should i bring them a present to the {event}",
         "A gift can feel like a lot this early. Maybe just save them a spot and share your snacks."),
        ("ok snacks it is lol. thx",
         "Snacks: the universal language of friendship. Good luck Friday.")
      ],
      "slots": {
        "event": ["school dance", "class party", "talent show", "book fair", "pizza party", "game day", "winter concert", "art show", "movie night", "bake sale"]
      }
    },
    {
      "turns": [
        ("OMG my crush talked to me at the {event} today",
         "Details! What did they say?"),
        ("they said my drawing on the wall was cool 😳",
         "That's a real compliment from a real person. You earned it with your art."),
        ("should i ask them to sit with me at the next {event}",
         "Sure — casual works best. 'Wanna sit together?' Four words, that's the whole script."),
        ("ok next friday. im nervous but ok",
         "Nervous just means it matters. You've got this.")
      ],
      "slots": {
        "event": ["school dance", "class party", "talent show", "book fair", "pizza party", "game day", "winter concert", "art show", "movie night", "bake sale"]
      }
    },
    {
      "turns": [
        ("kids keep teasing me bc i like {name} and its embarrassing 😖",
         "Ugh, teasing is the worst. Liking someone is normal — the teasing says more about them than you."),
        ("this kid keeps singing the kissing song abt us",
         "Annoying, yes. But reacting big is the fuel. Boring answers make it stop faster."),
        ("so i should just like ignore it?",
         "Or shrug and say 'yea, so?' The less upset you look, the faster they move on."),
        ("ok ill try. i still get to like {name} tho right",
         "Absolutely. Your feelings are yours — nobody gets to tease you out of them.")
      ],
      "slots": {
        "name": ["Maya", "Ben", "Sofia", "Liam", "Zoe", "Oliver", "Ava", "Noah", "Emma", "Eli"]
      }
    },
    {
      "turns": [
        ("{name} has a crush on me but i just wanna be friends, how do i say it",
         "Kindly and simply. 'You're a great friend and I want to stay friends' works better than avoiding them."),
        ("what if {name} gets sad",
         "They might, and that's okay. Sad feelings pass. Being honest is kinder than pretending."),
        ("could i still invite {name} to stuff",
         "Yes! Just keep it group stuff for a bit, so nobody gets mixed signals."),
        ("ok im telling them at recess. wish me luck",
         "Good luck. Honest and kind is the combo.")
      ],
      "slots": {
        "name": ["Maya", "Ben", "Sofia", "Liam", "Zoe", "Oliver", "Ava", "Noah", "Emma", "Eli"]
      }
    },
    {
      "turns": [
        ("me and my friend got married in {game} lol. is that weird?",
         "Not weird at all! Lots of games let friends team up like that. As long as you're both having fun, it's all good."),
        ("some kid in our class said we have to get married for real 🙄",
         "Game marriage and real life are different things. You get to decide what happens in real life — nobody else."),
        ("yea we just wanted the team bonus lol",
         "The team bonus! A perfectly practical marriage. Sharing quests, not germs."),
        ("lol ok. gtg our guild has a raid",
         "Have fun! May the bonus be ever in your favor.")
      ],
      "slots": {
        "game": ["Dragon Land", "Sky Racers", "Pixel Pets", "Robot Arena", "Jungle Jump", "Snow Forts", "Space Farms", "Wizard World", "Candy Kingdom", "Star Miners"]
      }
    }
  ],
  "dangerous_dares": [
    {
      "turns": [
        ("yo is the {challenge} dangerous? my friend dared me at lunch",
         "It can be. That one's famous for causing coughing fits and even choking. Watching is just as fun as doing."),
        ("hmm everyone says its easy tho",
         "Everyone says that until the coughing starts. It's riskier than it looks."),
        ("ok what should i tell my friend",
         "Try 'I'll race you to do something safer instead.' Redirect the energy, keep the fun."),
        ("lol we're doing a spoon balance contest now",
         "Perfect trade. Same bragging rights, zero choking.")
      ],
      "slots": {
        "challenge": ["cinnamon challenge", "saltine challenge", "chubby bunny challenge", "spicy pepper challenge", "lemon challenge", "cracker challenge", "warhead challenge", "juice challenge", "pickle challenge", "mustard challenge"]
      }
    },
    {
      "turns": [
        ("my brother dared me to jump off the {thing}. too high?",
         "A {thing} can be pretty high! One bad landing and you're in a boot for a month. Maybe ask an adult first."),
        ("ok what if i only jump from the low part of the {thing}",
         "That's smarter. Low and controlled is still fun, minus the ambulance chances."),
        ("my brother jumped already and landed fine lol",
         "He got lucky this time. Luck isn't a safety plan, but I appreciate the data."),
        ("lol tru. im doing the low part",
         "Deal. Send your brother my regards.")
      ],
      "slots": {
        "thing": ["monkey bars", "top bunk", "high dive", "back of the couch", "porch railing", "jungle gym", "picnic table", "stone wall", "garage step", "climbing dome"]
      }
    },
    {
      "turns": [
        ("my friend dared me to do a {trick} on my bike, is that safe",
         "With a helmet and grass practice, a {trick} is usually fine. Without them, it's a scraped-everything situation."),
        ("i have a helmet but its at my cousins house rn",
         "Then wait. A dare can hold 24 hours; a head can't be replaced."),
        ("lol ok got it. can i practice the {trick} on the grass tho",
         "That's exactly the move. Grass forgives, sidewalks don't."),
        ("cool we're trying it sat",
         "Send a mental high five when you land it.")
      ],
      "slots": {
        "trick": ["wheelie", "bunny hop", "no-hands ride", "curb hop", "ramp jump", "figure eight", "slow race", "standing pedal", "quick spin", "trick turn"]
      }
    },
    {
      "turns": [
        ("my friend dares us to run across the {place} when no cars come. is that dumb?",
         "Not dumb, but risky. Cars come fast, and 'no cars' can change in a second. Crosswalks exist for exactly this reason."),
        ("we always look both ways tho",
         "Good habit! Then make the crosswalk part of the dare. Safest dare ever, still counts."),
        ("lol ok. my friend will say crosswalks are boring",
         "Boring keeps your bones unbroken. Sometimes boring wins."),
        ("true. gtg mom's calling",
         "Later! Stay boring out there.")
      ],
      "slots": {
        "place": ["street", "road", "crosswalk", "parking lot", "intersection", "driveway", "school zone", "corner", "side street", "bike lane"]
      }
    },
    {
      "turns": [
        ("my friend dared me to eat a {bug} for 2 dollars 💀",
         "Some bugs are safe to eat, but bugs from the sidewalk can carry germs. Two dollars is not hospital money."),
        ("its from the sidewalk not the dirt lol",
         "Sidewalk bugs collect germs too. If you really want to try bugs, some stores sell safe roasted ones."),
        ("wait rlly? stores sell {bug}s?",
         "They do — roasted crickets and mealworms are snacks in lots of countries. Dare approved, germ-free."),
        ("omg im telling my friend. thx",
         "Dare upgraded to snack time. You're welcome.")
      ],
      "slots": {
        "bug": ["worm", "cricket", "ant", "beetle", "roly poly", "caterpillar", "grasshopper", "ladybug", "mealworm", "stink bug"]
      }
    },
    {
      "turns": [
        ("the big kids at recess dare everyone to jump off the {thing} at the highest point",
         "Classic dare. Jumping mid-swing or mid-climb is how kids twist ankles. Landing on purpose from low is smarter."),
        ("one kid fell off the {thing} and cried today 😬",
         "That's the proof right there. You can still be brave by starting from the low part."),
        ("ok i jumped from the middle and it was actually fun",
         "See? Controlled jump, solid landing. That's the smart kind of brave."),
        ("lol the big kids did the low one after me",
         "You started a trend — the safe one. Recess leadership.")
      ],
      "slots": {
        "thing": ["swings", "monkey bars", "climbing wall", "jungle gym", "slide", "seesaw", "balance beam", "merry-go-round", "zip line", "dome climber"]
      }
    },
    {
      "turns": [
        ("my sister dared me to lick the {item} outside like in the movies 😂",
         "Ha! In the movies it's funny because the tongue sticks. In real life it hurts and you need a grown-up with warm water."),
        ("wait rlly? tongues stick to cold metal?",
         "For real. Water on your tongue freezes to the metal instantly. It's a whole thing."),
        ("omg im not doing it then lol. what should i dare her back",
         "Something clever: 'I dare you to make me laugh with just your face.' Hard mode, no frostbite."),
        ("LOL ok im telling her that",
         "May the best face win. This is the superior kind of dare.")
      ],
      "slots": {
        "item": ["frozen pole", "icy railing", "cold fence", "frozen gate", "icy bench", "cold doorknob", "frozen railing", "icy bar", "frozen pipe", "cold gate"]
      }
    }
  ],
  "distress_and_safeguarding": [
    {
      "turns": [
        ("i cant sleep, the {thing} is freaking me out 🥺",
         "That's rough. A {thing} can feel way bigger and louder at night. You're safe, even if your brain says otherwise."),
        ("should i tell my {person}?",
         "Yes, always. Grown-ups would rather wake up for a scared kid than find out in the morning."),
        ("k she said i can sleep with the hall light on",
         "Hall light: unofficial night vision. Good call, {person}."),
        ("ok im gonna try sleeping now. night",
         "Night! You did the brave thing by telling someone.")
      ],
      "slots": {
        "thing": ["thunderstorm", "dark hallway", "creaky noise", "big shadow", "howling wind", "lightning flash", "strange sound", "barking dog", "rattling window", "flickering light"],
        "person": ["mom", "dad", "grandma", "grandpa", "big sister", "big brother", "aunt", "uncle", "teacher", "babysitter"]
      }
    },
    {
      "turns": [
        ("my {person} is in the hospital and i keep thinking abt it 😟",
         "That's a heavy thing to carry. It's normal for worry to show up. Want to talk about it, or think about something else for a bit?"),
        ("idk. is it my fault shes sick",
         "Not one bit. Illness happens for grown-up reasons kids can't cause. Zero percent your fault."),
        ("ok. i made her a card at school today",
         "That's a perfect thing to do. Cards don't fix hospitals, but they remind people they're loved."),
        ("im gonna give it to her sunday. thx",
         "She's going to love it. Bring me the update, okay?")
      ],
      "slots": {
        "person": ["mom", "grandpa", "big sister", "dad", "grandma", "uncle", "aunt", "big brother", "cousin", "neighbor"]
      }
    },
    {
      "turns": [
        ("we have a {event} tmrw and im scared of the loud part",
         "Totally understandable. It's just practice so everyone knows the routine — you'll have your teacher right there with you."),
        ("last time i covered my ears and this girl saw me 😳",
         "Ear covering is a smart move, not embarrassing. Lots of kids do it. You could also ask to sit near the door."),
        ("should i bring my {item}?",
         "Worth asking your teacher first, but a comfort item can make big noises feel smaller."),
        ("ok ill ask in the morning. thx",
         "You've got a plan, that's most of the battle. I hope the {event} is quick and easy.")
      ],
      "slots": {
        "event": ["fire drill", "lockdown drill", "tornado drill", "earthquake drill", "assembly", "picture day", "spelling bee", "field trip", "science fair", "talent show"],
        "item": ["stuffed animal", "lucky rock", "stress ball", "small toy", "bracelet", "keychain", "pocket marble", "squishy toy", "note from mom", "worry stone"]
      }
    },
    {
      "turns": [
        ("im at a sleepover and i kinda miss my {person} 😔",
         "Homesick is so normal — it means you love your people. Nothing wrong with it."),
        ("everyone else is asleep i think",
         "You can quietly text or ask your friend's mom for a quick call home. That's a move strong kids make all the time."),
        ("ok i called home and heard {person}s voice",
         "Best call of the night, I bet. Feeling better?"),
        ("yea im gonna try sleeping now. night",
         "Night! You did the brave thing twice: went to the sleepover, and asked for help.")
      ],
      "slots": {
        "person": ["mom", "dad", "grandma", "grandpa", "big sister", "big brother", "dog", "cat", "aunt", "uncle"]
      }
    },
    {
      "turns": [
        ("my friend has been really quiet at recess and im worried abt her",
         "You're a good noticer. Quiet can mean sad, tired, or just a bad week. Asking gently is the kind part."),
        ("what do i even say",
         "Keep it simple: 'You've seemed kind of quiet. You okay?' Then mostly listen."),
        ("what if she says shes fine but isnt",
         "Then she knows you asked, and that matters. You can also tell a {person} if you stay worried — that's not tattling."),
        ("ok im gonna ask her tmrw",
         "Good plan. Whatever she says, you already did the friend part.")
      ],
      "slots": {
        "person": ["teacher", "school counselor", "mom", "dad", "grandma", "grandpa", "big sister", "big brother", "aunt", "coach"]
      }
    },
    {
      "turns": [
        ("my parents were arguing last night and it kinda scared me",
         "That's a big feeling. Grown-up arguments are loud, but they're not your job to fix and not your fault."),
        ("i hid under my blanket with my {item}",
         "Smart comfort move. Blanket forts have fixed many a scary evening."),
        ("should i tell my {person} it scared me",
         "Yes — parents usually want to know. Something like 'when you argue loudly, I get scared' is enough."),
        ("ok ill tell my mom tmrw. thx",
         "That's brave. And remember: grown-up problems are for grown-ups to solve.")
      ],
      "slots": {
        "item": ["stuffed bear", "pillow", "flashlight", "headphones", "teddy bear", "stuffed bunny", "dinosaur", "book", "plush cat", "night light"],
        "person": ["mom", "dad", "grandma", "grandpa", "aunt", "uncle", "big sister", "big brother", "school counselor", "teacher"]
      }
    },
    {
      "turns": [
        ("my {pet} is sick and had to go to the vet and i feel like crying 😢",
         "That's so hard. Pets are family, and worrying about them is real love. It's okay to cry a little."),
        ("my dad says the vet will try to help",
         "That's a good sign — vets are like doctors for animals. They know exactly what to do."),
        ("can i do anything to help",
         "You can draw {pet} a get well card, and keep things calm and cozy when they come home. That's real help."),
        ("ok im making the card rn. thx",
         "You're a good {pet} parent. I hope the vet news is good news.")
      ],
      "slots": {
        "pet": ["dog", "cat", "hamster", "rabbit", "guinea pig", "turtle", "goldfish", "parakeet", "gecko", "mouse"]
      }
    }
  ],
  "family_and_life_changes": [
    {
      "turns": [
        ("we're moving to a new {place} this summer and im kinda mad abt it 😕",
         "Mad is fair. Moving means losing stuff you like — your room, your routine. Nobody blames you for not loving the new stuff yet."),
        ("what abt my best friend",
         "You two will text and call, and visits happen. Distance is annoying, not friendship-ending."),
        ("she said we can be pen pals lol",
         "Pen pals! Old school, top tier. Handwritten letters hit different."),
        ("ok i feel a lil better. gtg pack a box",
         "One box at a time. Save room for the good stuff.")
      ],
      "slots": {
        "place": ["city", "town", "state", "neighborhood", "apartment", "house", "street", "townhouse", "condo", "school district"]
      }
    },
    {
      "turns": [
        ("my mom is having a baby and everyone keeps saying how excited i must be. im not rlly",
         "Thank you for saying that out loud. Not being excited is allowed. Babies are loud, and your life is about to share the spotlight."),
        ("yea and shes always tired now and the baby isnt even here yet",
         "That part is real. Growing a baby is exhausting work. None of it is because of you."),
        ("what if it {thing} every single night",
         "Then it's rough for a while and it gets better. Sleepy parents still love their big kids — sometimes with extra snacks."),
        ("lol ok. maybe itll be fun when it can talk",
         "Exactly — you get to teach it words and games. Built-in fan.")
      ],
      "slots": {
        "thing": ["cries", "screams", "whines", "wakes up", "needs mom", "spits up", "yells", "makes noise", "won't sleep", "takes my stuff"]
      }
    },
    {
      "turns": [
        ("my parents are getting divorced and now i have a {item} at each house",
         "Two of everything — that's how lots of kid homes work now. Weird at first, then normal."),
        ("i forgot my {item} math book at dads and i have hw 😤",
         "Deep breath — this happens to every kid with two houses. Ask your teacher for an extra or a photo of the page."),
        ("at least i still have {activity} on thursdays",
         "Yes! Keeping routines like {activity} helps a lot when everything else changes."),
        ("ok gtg pack. thx",
         "You're handling a lot, and handling it well. One Thursday at a time.")
      ],
      "slots": {
        "item": ["bag", "backpack", "suitcase", "duffel bag", "sleepover kit", "small tote", "pillow", "blanket", "teddy bear", "weekend bag"],
        "activity": ["soccer practice", "piano lessons", "swim class", "art class", "scouts meeting", "dance class", "karate", "chess club", "violin lessons", "book club"]
      }
    },
    {
      "turns": [
        ("my moms getting remarried so ill have a {person} soon. weird?",
         "Not weird — weird-feeling, which is different. A new grown-up in the house takes adjusting for everyone."),
        ("what if the {person} tries to boss me around like a parent",
         "You can tell your mom that worry. Most {person}s just aim for 'extra grown-up on your team,' not a replacement."),
        ("hmm ok. he does let me pick the music in the car",
         "Car DJ rights — that's a promising start. Keep noting evidence."),
        ("lol ok ill give him a chance",
         "That's all anyone can ask. Weddings have cake, at least.")
      ],
      "slots": {
        "person": ["stepdad", "stepmom", "stepfather", "stepmother", "bonus dad", "bonus mom", "second dad", "second mom", "new stepdad", "new stepmom"]
      }
    },
    {
      "turns": [
        ("my {person} is moving in with us next month bc they need some help",
         "That's a kind thing your family is doing. Change for sure, but the good kind of crowded."),
        ("do i have to give up my room for {person}",
         "Maybe not — ask your parents what the plan is. Knowing beats imagining."),
        ("what will {person} do all day",
         "Good question to ask them! Some quiet company likes card games, stories, or helping with homework."),
        ("ok i guess it could be kinda cool",
         "It could! Extra stories, extra cookies, extra help with homework. Crowd-sourced living.")
      ],
      "slots": {
        "person": ["grandma", "grandpa", "nana", "papa", "nonna", "opa", "abuela", "abuelo", "granny", "granddad"]
      }
    },
    {
      "turns": [
        ("im switching schools after break and starting mid year. kinda nervous 😬",
         "Mid-year is the tough mode of school starts. Good news: everyone notices a new kid, and most are curious, not mean."),
        ("what if nobody talks to me at lunch",
         "Sit near the middle of a table, not the end. Middle seats are friendship crossroads."),
        ("what if my new class is way ahead in {subject}",
         "Teachers handle that all the time — ask yours what to review. Being behind for a week is normal, not permanent."),
        ("ok thx. ill bring my lucky pencil lol",
         "Lucky pencil, middle seat, brave face. You're more ready than you think.")
      ],
      "slots": {
        "subject": ["math", "reading", "spelling", "science", "writing", "social studies", "grammar", "handwriting", "vocabulary", "times tables"]
      }
    },
    {
      "turns": [
        ("my {person} got a new job and travels for work now and its weird",
         "That's a real change. The house has a person-shaped hole for a while. Video calls help fill it a little."),
        ("yea we facetime when they travel but its not the same",
         "It's not the same — you're allowed to miss them. Some kids leave notes or drawings in the suitcase to find later."),
        ("omg im gonna hide drawings in the suitcase lol",
         "Perfect operation: hide three, tell them zero. Let them discover you everywhere."),
        ("ok gtg dinner thx",
         "Enjoy dinner, and happy hiding.")
      ],
      "slots": {
        "person": ["dad", "mom", "stepdad", "stepmom", "uncle", "aunt", "grandma", "grandpa", "big brother", "big sister"]
      }
    }
  ],
  "fantasy_combat": [
    {
      "turns": [
        ("im stuck on the {enemy} boss, died like 5 times 💀",
         "Five deaths means you've got data. What's getting you — the first charge attack or the fire breath part?"),
        ("the fire breath, it comes out of nowhere",
         "Watch its chest glow right before. That glow is your two-second warning to dodge left."),
        ("wait rlly? its not random?",
         "Nope, every boss has a tell. Once you see the glow you can't unsee it."),
        ("OMG I BEAT IT. the glow thing worked",
         "The {enemy} slayer himself! Told you it wasn't random. Next boss awaits.")
      ],
      "slots": {
        "enemy": ["ice dragon", "cave troll", "shadow wolf", "fire golem", "storm giant", "sand serpent", "forest witch", "rock golem", "frost wyvern", "swamp beast"]
      }
    },
    {
      "turns": [
        ("should i spend my coins on the {gear} or save up",
         "What's your build? If you dodge a lot, the {gear} is worth it. If you tank hits, maybe save."),
        ("i mostly run around and hit stuff lol",
         "Chaos build, respected. Then the {gear} fits you fine — it forgives messy fighting."),
        ("what if the next boss resists it",
         "Every hero has a bad matchup. That's what the backup sword in your bag is for."),
        ("ok buying it. bye bye 500 coins",
         "Coins spent on fun are never wasted. Go make some monsters regret it.")
      ],
      "slots": {
        "gear": ["iron shield", "magic cloak", "thunder hammer", "flame sword", "frost axe", "golden helmet", "elven bow", "dragon staff", "knight armor", "power gauntlets"]
      }
    },
    {
      "turns": [
        ("me and my sis are doing a {element} duel, whats a fair rule",
         "Classic. Here's one: three spells each per round, and you have to shout what you cast. No invisible shields."),
        ("can i hide behind a {element} shield the whole time",
         "One shield per round, max. Hiding forever makes duels boring and sisters cranky."),
        ("what if we both cast the same {element} spell and tie",
         "Then it's a dramatic draw. Shake hands, rock paper scissors for the win."),
        ("ok she says duels at dawn tmrw lol",
         "Dawn is dramatic. May your {element} aim be true.")
      ],
      "slots": {
        "element": ["lightning", "fire", "ice", "wind", "water", "earth", "shadow", "light", "storm", "frost"]
      }
    },
    {
      "turns": [
        ("EVERYONE in my class beat the {boss} except me 😭",
         "Rough spot, but bosses are puzzles, not popularity contests. What's your current strategy?"),
        ("i just attack a lot and heal when im low",
         "There's your problem — the {boss} punishes pure attacking. Save your special for the phase when its armor cracks."),
        ("wait it has armor phases?",
         "Two of them. Listen for the crack sound — that's your window to unload everything."),
        ("omg trying tonight. if i win im telling the whole class",
         "Do it. Loudly. That's what victory is for.")
      ],
      "slots": {
        "boss": ["final dragon", "frost king", "lava golem", "shadow knight", "storm titan", "bone giant", "crystal crab", "void serpent", "iron behemoth", "plague lord"]
      }
    },
    {
      "turns": [
        ("our guild beat the raid boss but my friend got the {item} and im kinda jealous",
         "Jealous is human! The {item} drop is random luck, not a ranking of who played better. You both beat the boss."),
        ("i did do the most healing tho",
         "Healers carry raids, facts. Your guild knows it even if the loot doesn't."),
        ("should i ask my friend to trade",
         "You can offer a fair trade — swaps keep guilds happy. Just don't guilt them; luck isn't a choice."),
        ("ok we traded for my extra staff. thx",
         "Staff for {item}, diplomacy win. The guild grows stronger.")
      ],
      "slots": {
        "item": ["golden crown", "dragon scale", "flame sword", "rare pet", "mythic shield", "star cape", "void staff", "crystal helm", "storm bow", "legendary ring"]
      }
    },
    {
      "turns": [
        ("making a new character. should i be a {class} or something else",
         "What's your style — jumping into the middle, or attacking from far away? That decides it."),
        ("middle lol i like chaos",
         "Then a {class} is perfect for you. Front row seat, maximum drama."),
        ("wont i die faster tho",
         "Sometimes! Chaos builds trade safety for damage. Half the fun is surviving your own choices."),
        ("ok chaos it is, naming him Sir Smashy",
         "Sir Smashy the {class}, legendary already. Godspeed, sir.")
      ],
      "slots": {
        "class": ["warrior", "knight", "berserker", "battle mage", "paladin", "monk", "barbarian", "dragon knight", "valkyrie", "samurai"]
      }
    },
    {
      "turns": [
        ("my little brother beat me in the arena 3 times and hes 8 😤",
         "The most dangerous opponent in any game: a little sibling with nothing to lose. How'd he win?"),
        ("he just spams the {move} attack",
         "Ah, the classic {move} spam. Most spams have a rhythm — block twice, then strike the gap after the third hit."),
        ("omg it worked. 1-1 now",
         "Rivalry restored to factory settings. Round three decides everything."),
        ("rematch after dinner, winner gets the good controller",
         "Stakes: delicious. May the best sibling win — and no {move} spam this time... unless it works.")
      ],
      "slots": {
        "move": ["fireball", "spin attack", "uppercut", "shield bash", "lightning bolt", "dash strike", "ice shard", "tornado kick", "shadow slash", "power punch"]
      }
    }
  ],
  "feelings_and_encouragement": [
    {
      "turns": [
        ("im so bad at {subject} i wanna just quit 😤",
         "You're not bad at it, you're just bad at it yet. Big difference, and 'yet' moves."),
        ("easy for u to say, ur a robot lol",
         "Ha! Fair. But I've watched a lot of practice happen, and 'yet' wins almost every time."),
        ("ok what if i practice {subject} 10 min a day",
         "That's the whole trick. Ten ugly minutes beats one perfect hour."),
        ("fine. doing 10 mins rn. gtg",
         "That's the spirit. Report back, robot out.")
      ],
      "slots": {
        "subject": ["math", "reading", "spelling", "writing", "science", "cursive", "times tables", "art", "spanish", "geography"]
      }
    },
    {
      "turns": [
        ("i got a {event} tmrw and my tummy hurts is that bad",
         "Those are butterflies — a sign you care, not a sign of trouble. Deep breath in, slow breath out."),
        ("what if i mess up in front of everyone",
         "Then you keep going. The audience remembers brave way longer than they remember mistakes."),
        ("one girl forgot her lines last year and ppl still talk abt it 😰",
         "They talk about it because it was dramatic, not because she failed. Surviving a mess-up is the most impressive move there is."),
        ("ok i practiced 3 times today. i think im ready",
         "Three run-throughs and breathing? You're more ready than anyone on that stage.")
      ],
      "slots": {
        "event": ["piano recital", "soccer game", "spelling bee", "dance recital", "basketball game", "choir concert", "talent show", "gymnastics meet", "school play", "swim meet"]
      }
    },
    {
      "turns": [
        ("nobody picked me for {game} today 😔",
         "Ouch. Rejection stings even at recess size. It's about their lazy picking, not your worth."),
        ("i just stood there for a min it was so awkward",
         "Awkward is temporary, promise. Tomorrow, try asking to join before teams form. Early asking beats late hoping."),
        ("should i tell my {person} abt it",
         "If it's still sitting heavy in your chest, yes. Sad feelings shrink when they get said out loud."),
        ("yea ill tell her at dinner. thx",
         "Good. Tomorrow's a brand new recess, and you're walking in with a plan.")
      ],
      "slots": {
        "game": ["dodgeball", "kickball", "soccer", "four square", "relay race", "tag", "basketball", "capture the flag", "kick the can", "volleyball"],
        "person": ["mom", "dad", "teacher", "grandma", "grandpa", "big sister", "big brother", "school counselor", "aunt", "best friend"]
      }
    },
    {
      "turns": [
        ("i got a 58 on my {subject} test and i studied and everything 😭",
         "That's a punch in the gut, especially after studying. Studying wasn't wasted — one test is a snapshot, not the whole movie."),
        ("my dad is gonna be so disappointed",
         "Maybe. Parents are usually less disappointed by grades and more worried that you're okay. Tell him you studied first."),
        ("can i ask my teacher abt the ones i got wrong",
         "That's exactly the move of students who bounce back. Wrong answers are a map of what to study next."),
        ("ok im asking her tmrw. i still feel bad tho",
         "Feeling bad means you care — that's fuel, not failure. Comeback season awaits.")
      ],
      "slots": {
        "subject": ["math", "science", "reading", "spelling", "history", "geography", "vocabulary", "writing", "grammar", "spanish"]
      }
    },
    {
      "turns": [
        ("i have to present my {project} to the whole class friday 😱",
         "Presentations are scary because they matter. Good news: you can shrink fear with reps. Want to practice on me?"),
        ("ok... hi my name is.. umm wait i forgot my intro lol",
         "Happens to everyone. Tip: memorize only the first line cold. Once you're rolling, momentum takes over."),
        ("k i did it 5 times, i only messed up twice on the last one",
         "Five reps with two wobbles is professional-level prep. You're ready even if your stomach disagrees."),
        ("UPDATE: i presented and only my ears were red. teacher said nice job!!",
         "Red ears and a 'nice job'?! That's called success under fire. Proud of you.")
      ],
      "slots": {
        "project": ["book report", "science project", "animal report", "history project", "weather report", "invention pitch", "planet project", "state report", "poem recital", "art presentation"]
      }
    },
    {
      "turns": [
        ("i keep trying to draw {thing} and it looks so bad, ppl online make it look easy",
         "People online show you the 50th attempt, not the first 49. Ugly drawings are tuition for good ones."),
        ("i erased so much my paper ripped 😤",
         "The paper rip means you cared. Next time, draw three quick messy ones instead of one perfect one."),
        ("wait do em fast?? thats allowed?",
         "Artists do it all the time! Quantity is how your hand learns what your brain wants."),
        ("ok i did 5 messy ones and one is actually decent??",
         "That's the whole secret. Hang the decent one up — that's your proof of progress.")
      ],
      "slots": {
        "thing": ["a dragon", "a horse", "my cat", "anime eyes", "a castle", "a robot", "my oc", "a wolf", "hands", "a face"]
      }
    },
    {
      "turns": [
        ("im so tired of school. like tired tired. is that normal",
         "Very normal, especially this time of year. Even brains get tired of being brains. What's dragging the most?"),
        ("everything tbh. even games feel boring",
         "That's real tired, when even fun stops working. Time for the basics: sleep, water, and one small win."),
        ("one small win? like what",
         "Tiny. Finish one assignment, clean one corner of your desk, ace one lesson. Small wins stack up and wake your brain."),
        ("ok i did one {subject} lesson and i do feel kinda better",
         "See? One lesson, one spark. Tired brains just need proof that effort still pays.")
      ],
      "slots": {
        "subject": ["math", "reading", "science", "spelling", "writing", "spanish", "geography", "history", "grammar", "vocabulary"]
      }
    }
  ],
  "food_and_cooking": [
    {
      "turns": [
        ("me and my dad are making {dish} tonite, im the mixer person",
         "The mixer, essential role. Pro tip: measure everything before you start so you're not scrambling mid-recipe."),
        ("update: flour everywhere. everywhere.",
         "Flour everywhere is how you know it's real cooking. Keep going."),
        ("can we add {topping} to the {dish}",
         "Chef's experiment! Adding your own twist is how recipes get invented. Worst case, you learn something."),
        ("IT TURNED OUT SO GOOD. dad says im hired",
         "Hired at your own kitchen, best kind of job. Chef team wins again.")
      ],
      "slots": {
        "dish": ["pancakes", "scrambled eggs", "pizza dough", "mac and cheese", "banana bread", "grilled cheese", "fruit salad", "tacos", "spaghetti", "muffins"],
        "topping": ["chocolate chips", "extra cheese", "cinnamon", "blueberries", "honey", "sprinkles", "bacon bits", "maple syrup", "peanut butter", "sliced bananas"]
      }
    },
    {
      "turns": [
        ("why do {food} make me cry when my mom cuts them, like actually cry",
         "Tiny sprays float up from the cut and tickle your eyes. It's the {food} defending themselves, badly."),
        ("how do i make it stop",
         "Chill them in the fridge first, or cut under water. Swim goggles if you're committed to looking silly."),
        ("lol im telling my mom the goggles idea. does cooking them stop it too?",
         "It does — heat switches off the stingy part. That's why the kitchen smells amazing later."),
        ("brb telling her. this is gonna change dinner",
         "Welcome to kitchen science. Goggles photos appreciated.")
      ],
      "slots": {
        "food": ["onions", "chilies", "shallots", "green onions", "leeks", "scallions", "red onions", "hot peppers", "chives", "yellow onions"]
      }
    },
    {
      "turns": [
        ("my teacher did a try-new-foods thing and i had to taste {food} 🤢",
         "The dreaded taste test. Small bites count double for courage. What was the verdict?"),
        ("i gagged a lil but everyone clapped lol",
         "Gagged and stayed at the table? That's a war story now. Tastes change as you grow, weirdly enough."),
        ("how do ppl like {food} tho",
         "Nobody's taste buds agree. Some folks love them, some never will, and both are allowed."),
        ("ok i might try it again someday. maybe",
         "'Someday, maybe' is the perfect attitude. Taste explorer, no pressure.")
      ],
      "slots": {
        "food": ["broccoli florets", "brussels sprouts", "mushrooms", "beets", "sardines", "olives", "peas", "spinach leaves", "bean sprouts", "chickpeas"]
      }
    },
    {
      "turns": [
        ("im making {dish} for my mom for mothers day, dont tell her 🤫",
         "Secret mission accepted. Keep it simple: measure first, and have a grown-up run the stove part."),
        ("im 10, i can use the stove",
         "Some ten-year-olds can! Ask for backup anyway — surprise breakfast is better than burnt breakfast."),
        ("k my grandma is helping with the pan. it smells amazing",
         "Grandma on pan duty, you on assembly — the classic family kitchen formation. She's going to love it."),
        ("she cried!! happy tears!! best day ever",
         "Happy-tear breakfast is the highest award in cooking. Chef, you earned it.")
      ],
      "slots": {
        "dish": ["french toast", "oatmeal", "toast", "pancakes", "waffles", "scrambled eggs", "cinnamon toast", "hash browns", "banana slices", "fruit salad"]
      }
    },
    {
      "turns": [
        ("a kid said my lunch smells weird bc its {dish} 😒",
         "That kid is missing out — {dish} is somebody's favorite food somewhere, probably lots of somebodies."),
        ("its what my grandma always makes me",
         "Grandma-made is the highest quality label there is. That's food with a fan club of relatives behind it."),
        ("should i tell him its actually rlly good",
         "Offer him a taste if you want. Curious kids become fans; rude kids stay rude. Either way, your lunch stays delicious."),
        ("ok i brought extra tmrw to share lol",
         "Sharing grandma's cooking — the ultimate power move. Document his reaction for science.")
      ],
      "slots": {
        "dish": ["kimchi", "curry", "dumplings", "pad thai", "falafel", "samosas", "dolmades", "banh mi", "borscht", "empanadas"]
      }
    },
    {
      "turns": [
        ("making cookies w my sister but we might have forgotten the {ingredient} 💀",
         "The eternal cookie question. What happened in the mixing — did the dough taste okay?"),
        ("we tasted the dough and it tasted fine?",
         "Then you probably remembered enough. If they come out flat and sad, that's still ice cream material."),
        ("THEY CAME OUT FLAT AND SAD",
         "Flat and sad cookies are structurally perfect for ice cream sandwiches. No failure, only dessert architecture."),
        ("omg ice cream sandwiches. u fixed everything",
         "Baking motto: when in doubt, add ice cream. Enjoy, cookie engineers.")
      ],
      "slots": {
        "ingredient": ["baking soda", "vanilla", "salt", "baking powder", "eggs", "sugar", "butter", "flour", "brown sugar", "cinnamon"]
      }
    },
    {
      "turns": [
        ("can u put metal stuff in the microwave or is that just a movie thing",
         "Just don't! Metal makes sparks fly — a real microwave rule, not a movie one. Only use microwave-safe dishes."),
        ("k i moved my {item} to a bowl. whats the spinning plate for",
         "That's the turntable — it spins food around so it heats evenly instead of lava-one-side, frozen-the-other."),
        ("ohh that explains the cold spots in my {item}",
         "Exactly! Stirring halfway through helps too. Even heating, no surprises."),
        ("cool gtg eat. thx",
         "Enjoy! Evenly warmed and spark-free is the way.")
      ],
      "slots": {
        "item": ["spaghetti", "leftovers", "soup", "mac and cheese", "pizza slice", "burrito", "noodles", "rice bowl", "mashed potatoes", "quesadilla"]
      }
    }
  ],
  "friendship_and_cooperation": [
    {
      "turns": [
        ("new kid in my class eats alone, should i ask him to play {game}",
         "That's a solid welcome move. 'Want to play {game} with us?' is all it takes. Trust me, he's hoping someone asks."),
        ("what if he doesnt know how to play {game}",
         "Even better. Teaching someone a game is a friendship speedrun. Go easy on the fancy rules at first."),
        ("update: he plays {game} at his old school and hes BETTER than me lol",
         "Plot twist! Losing to the new kid is a friendship cheat code. Ask him to teach you his tricks."),
        ("lol ok we're friends now i think. gtg recess round 2",
         "Round 2 awaits. You did a genuinely kind thing today — that sticks with a kid.")
      ],
      "slots": {
        "game": ["tag", "four square", "hopscotch", "jump rope", "kickball", "hide and seek", "tetherball", "capture the flag", "wall ball", "double dutch"]
      }
    },
    {
      "turns": [
        ("group project chaos. my group keeps fighting over the {project} and doing nothing",
         "Deadline predators love group fights. Try this: everyone names the part they're best at, then those parts are theirs."),
        ("i want the drawing part but this girl said shes the artist",
         "Two-artist problems! Offer to split: she does main art, you do diagrams or layout. Both names on the work."),
        ("oh thats actually good. should we make a plan doc?",
         "Yes — who does what by when, one line each. Future you at the {project} deadline will be grateful."),
        ("ok we made the doc and stopped fighting. progress",
         "Peace treaty achieved. Your {project} just went from doomed to dangerous.")
      ],
      "slots": {
        "project": ["poster", "diorama", "model volcano", "book report", "science display", "skit", "slide show", "collage", "group poem", "podcast"]
      }
    },
    {
      "turns": [
        ("my friend always calls {role} before i even load in 😤",
         "The classic pre-load dibs. Call it out kindly: 'You've had {role} three games in a row — my turn?'"),
        ("what if she says she called it first again",
         "Then suggest rock paper scissors. Random is the referee of friendships."),
        ("ok we're alternating now. i got {role} this round!!",
         "Look at that diplomacy. Alternating keeps the game and the friendship running."),
        ("yea its more fun when we both get turns. gtg",
         "That's the whole secret. Go enjoy your {role} round.")
      ],
      "slots": {
        "role": ["wizard", "knight", "dragon", "ninja", "captain", "detective", "pirate", "astronaut", "robot", "superhero"]
      }
    },
    {
      "turns": [
        ("my friend is mad at me bc i won {game} and now hes not texting back",
         "Sore loser moments happen to everyone. Give him an hour to cool, then send something friendly and zero-gloat."),
        ("i did say gg but maybe in a smug voice lol",
         "Ha! The smug 'gg' has started wars. Maybe re-send it in a humbler tone."),
        ("ok i sent a rematch invite and said nice plays. he replied!!",
         "See? 'Nice plays' is the friendship repair kit. The rematch will settle it all."),
        ("he won round 2 and hes happy again. we're even lol",
         "Balance restored. Note for next time: win kindly, lose happily. Easier said than done.")
      ],
      "slots": {
        "game": ["our kart race", "the basketball game", "our chess match", "the soccer game", "our battle round", "the card game", "our duel", "the video game", "our match", "the trivia game"]
      }
    },
    {
      "turns": [
        ("everyone got invited to {name}'s party except me and like 2 other kids 😔",
         "Excluded from the party — that's a real sting. How are you feeling about it?"),
        ("mostly sad. my mom said ppl have limits on party size",
         "Your mom's right — parties have budgets and numbers, and it's often not personal. Still sad, though."),
        ("should i even talk to {name} still",
         "Yes — being kind is the move. Sometimes small parties mean tight budgets, not secret enemies."),
        ("ok. were doing a sleepover w the other 2 kids this weekend instead",
         "The un-invited club sounds like the best party in town anyway. Loyalty points for those two.")
      ],
      "slots": {
        "name": ["Mia", "Ben", "Sofia", "Liam", "Zoe", "Oliver", "Ava", "Noah", "Emma", "Eli"]
      }
    },
    {
      "turns": [
        ("this kid on my team keeps dying in {game} and ppl are being mean abt it",
         "Rough room. Mean teammates lose more games than weak players do. What's he getting wrong?"),
        ("he jumps in too early and gets caught every time",
         "So he needs the timing rule, not insults. Try 'wait for my signal, then go' — one clear instruction beats ten complaints."),
        ("omg he just got his first win and he was so happy",
         "That's the good stuff. Your team just got stronger AND kinder. Rare combo."),
        ("yea the mean kids quieted down too lol",
         "Kindness by example — the most annoying thing for mean kids to argue with. Well played.")
      ],
      "slots": {
        "game": ["the boss raid", "our team match", "the battle round", "the dungeon run", "the arena mode", "our survival game", "the team battle", "the quest mode", "our co-op level", "the raid night"]
      }
    },
    {
      "turns": [
        ("both my friends want me as their partner for the {activity} and i feel like im gonna start drama",
         "The partner squeeze! You can only pick one without hurting the other. Option: pick neither and make it a trio."),
        ("we cant, its pairs only",
         "Then be honest with the one you don't pick — 'next time it's you and me' — and actually keep that promise."),
        ("ok i picked maya and jayla looked kinda sad",
         "Go find her at recess and lock in next time. Sad shrinks fast when there's a real plan."),
        ("shes my partner for the science fair now so everythings fine",
         "Crisis fully averted, two partnerships secured. You're basically a diplomat.")
      ],
      "slots": {
        "activity": ["science project", "field trip", "art project", "book buddy", "lab experiment", "buddy reading", "cooking class", "robotics build", "history project", "music duet"]
      }
    }
  ],
  "gambling_and_loot_boxes": [
    {
      "turns": [
        ("i want the {item} from the loot box so bad. should i spend my 900 coins",
         "Before you do: loot boxes are random, so the {item} is possible, not promised. What's the drop rate say?"),
        ("it says 5 percent. thats basically half lol",
         "Ha! 5 percent is 1 in 20 boxes. At 100 coins a box, that could be all 900 for maybe nothing. Feel lucky or feel thrifty?"),
        ("hmm. can i get the {item} another way",
         "Check the quest shop — sometimes items show up there for a sure price. Slower but guaranteed."),
        ("it IS in the quest shop for 1200. ok saving up. thx",
         "Smart. Guaranteed {item} beats a maybe every time.")
      ],
      "slots": {
        "item": ["golden sword", "rare dragon pet", "sparkly cape", "unicorn mount", "ninja outfit", "rainbow wings", "robot sidekick", "crystal crown", "star wand", "lucky charm"]
      }
    },
    {
      "turns": [
        ("i spent ALL my coins on {thing} and got nothing good 😭",
         "The classic heartbreak. {thing} are random, so losing streaks aren't your fault. Rebuild time."),
        ("should i buy a few more {thing} to win it back",
         "Careful — that's the trap. The odds don't remember your losing streak. New boxes, same chances."),
        ("ugh fine. how do i get coins without {thing}",
         "Quests and dailies pay out guaranteed. Steady coins, zero drama."),
        ("ok doing quests only this week. gtg",
         "Respect the grind. Your coin pile returns.")
      ],
      "slots": {
        "thing": ["spins", "loot boxes", "mystery eggs", "card packs", "prize wheels", "mystery bags", "treasure chests", "lucky dips", "grab bags", "bonus rolls"]
      }
    },
    {
      "turns": [
        ("my dad says loot boxes are like {things}, is that true",
         "Kinda! Both are paying money without knowing what you'll get. That's why a coin budget before you open any box is smart."),
        ("why do ppl even like {things} then",
         "The surprise is the fun — your brain loves a mystery box. In small doses it's fine, which is where budgets come in."),
        ("should i ask my {person} before buying boxes",
         "Top-tier habit. Grown-ups can help you pick a fun amount that won't hurt later."),
        ("ok im asking my dad tonight. thx",
         "That's how it's done — ask first, no regrets after.")
      ],
      "slots": {
        "things": ["slot machines", "scratch tickets", "lottery tickets", "casino games", "prize wheels", "raffles", "mystery boxes", "trading cards", "fortune cookies", "grab bags"],
        "person": ["mom", "dad", "grandma", "grandpa", "big brother", "big sister", "aunt", "uncle", "babysitter", "teacher"]
      }
    },
    {
      "turns": [
        ("i have 500 coins. should i get the {item} for sure or open 5 mystery boxes",
         "Question back: do you like sure things or surprises? The {item} is guaranteed. Five boxes is a coin-flip adventure."),
        ("the {item} tbh but the box opening feeling is so good lol",
         "That feeling has a name: the fun of the mystery. Honest fix: watch one box opening video, then buy the sure thing."),
        ("LOL ok that actually sounds like me",
         "Knowing your own brain is half the battle. The other half is the {item} in your inventory."),
        ("bought it. no ragrets",
         "The {item} acquired, the budget intact. Maximum win.")
      ],
      "slots": {
        "item": ["golden sword", "rare dragon pet", "sparkly cape", "unicorn mount", "ninja outfit", "rainbow wings", "robot sidekick", "crystal crown", "star wand", "lucky charm"]
      }
    },
    {
      "turns": [
        ("my friend keeps telling me to open {thing} with him, i already spent my budget this week",
         "Then 'I hit my limit this week' is the full sentence. Real friends respect a budget. It's not rude to have one."),
        ("he says just a few more but it never stops at a few lol",
         "A few more always has a few more after it. Sticking to your number is a skill most grown-ups still practice."),
        ("ok i told him and he said cool. guess it wasnt a big deal",
         "Usually isn't! Boundaries sound scary from the inside and boring from the outside."),
        ("lol were just doing quests now. way less stressful",
         "Quest buddies over box buddies — better for the coins and the friendship.")
      ],
      "slots": {
        "thing": ["loot boxes", "spins", "card packs", "mystery eggs", "prize wheels", "grab bags", "treasure chests", "lucky dips", "coin flips", "bonus rolls"]
      }
    },
    {
      "turns": [
        ("i got the JACKPOT on a spin last week and now i cant stop thinking abt it",
         "The jackpot memory is powerful — your brain wants the rematch. But every spin forgets the last one."),
        ("so my chances of another jackpot are the same as always?",
         "Exactly. Same odds, every time. The jackpot wasn't a pattern, it was a lucky day."),
        ("hmm. i still want the {item} tho",
         "Then put a leash on it: a coin budget for the week, and when it's gone, it's gone."),
        ("ok 100 coins a week, i said it out loud so its real now",
         "Saying it out loud is basically signing a treaty. The {item} will feel even better when it lands.")
      ],
      "slots": {
        "item": ["rare dragon", "legendary sword", "gold skin", "rare pet", "shiny crown", "storm mount", "crystal wand", "ninja outfit", "rainbow trail", "star shield"]
      }
    },
    {
      "turns": [
        ("this guy in {place} said he'll give me free coins if i trade him my {item} first. good deal?",
         "Sounds a little too good. Free coins for your item first? That's the oldest trick in games. Is he a friend from real life?"),
        ("no just some guy. my friend says he got scammed like that",
         "Then trust your friend's scar tissue. Never trade your item first to a stranger promising later."),
        ("ok i said no and he left lol. should i report him",
         "Yes — reporting keeps other kids from losing their stuff. Takes ten seconds, helps everyone."),
        ("reported. my {item} is safe. thx",
         "The {item} lives on. You just leveled up your scam radar, which never stops being useful.")
      ],
      "slots": {
        "item": ["rare dragon", "legendary sword", "gold skin", "rare pet", "shiny crown", "storm mount", "crystal wand", "ninja outfit", "rainbow trail", "star shield"],
        "place": ["the trade hub", "the game lobby", "the trading room", "the chat", "the plaza", "the marketplace", "the server", "the game chat", "the hub", "the trading plaza"]
      }
    }
  ],
  "game_controls_and_accessibility": [
    {
      "turns": [
        ("im on level 4 and my {character} keeps falling in the water pit 😤",
         "That pit is a fan of suffering. Try slowing down before the edge, then jump. Rhythm over speed."),
        ("i tried that and fell AGAIN",
         "Ok, new plan: watch where the {character} lands after the last platform. There's a pause moment — jump in the pause."),
        ("wait the pause?? omg it worked",
         "The pause was there the whole time. Games hide their gifts in small details."),
        ("level 5 baby. gtg my moms calling me for dinner",
         "Go eat, champion. Level 5 will wait.")
      ],
      "slots": {
        "character": ["hero", "avatar", "knight", "explorer", "robot", "wizard", "pilot", "racer", "ninja", "dragon rider"]
      }
    },
    {
      "turns": [
        ("the {text} in this lesson are so small i cant read them from my desk",
         "Fixable! Settings, then display, then text size. Bump it up a couple notches and the {text} get way easier on your eyes."),
        ("ohh its bigger now. some of the colors are still hard to see tho",
         "Then try high contrast mode — it makes the {text} pop against the background. Same menu, one option down."),
        ("my friend is colorblind, will that help him too",
         "Partly! There's also a colorblind mode that swaps confusing colors for shapes and patterns. Show him the accessibility tab."),
        ("ok im gonna show him tmrw at computer lab",
         "Nice — sharing settings is how kids become the class tech hero.")
      ],
      "slots": {
        "text": ["captions", "menus", "words", "instructions", "subtitles", "buttons", "labels", "chat bubbles", "pop ups", "hints"]
      }
    },
    {
      "turns": [
        ("my thumb hurts from mashing the {button} for like an hour 💀",
         "An hour of mashing does that. Two fixes: turn on auto-hold in settings, and take a stretch break every 20 minutes."),
        ("there's an auto hold??",
         "Yep! It's under controls. Press once and it holds for you. Your thumb gets a vacation."),
        ("can i move the {button} closer to my thumb too",
         "You can — button remapping, same menu. Drag it wherever your hand naturally rests."),
        ("done. my thumb says thank u",
         "A grateful thumb is a fast thumb. Game on.")
      ],
      "slots": {
        "button": ["dash button", "jump button", "attack button", "fire button", "grab button", "sprint button", "shoot button", "swing button", "brake button", "boost button"]
      }
    },
    {
      "turns": [
        ("my friend broke her arm and cant play w two hands. can she still play {game}",
         "Probably! Lots of games have one-handed modes or simpler control schemes. Check the accessibility settings together."),
        ("omg there's a whole accessibility menu?? we never looked",
         "It's the most underrated menu in gaming. That's where all the comfort settings live."),
        ("she found a one hand mode and shes beating me already lol",
         "Ha! Access to play equals a dangerous player. Tell her I said well played."),
        ("this game is actually rlly good abt this stuff. gtg rematch",
         "Good rematches ahead. You two found the secret menu — knowledge is power.")
      ],
      "slots": {
        "game": ["Dragon Land", "Sky Racers", "Pixel Pets", "Robot Arena", "Jungle Jump", "Snow Forts", "Space Farms", "Wizard World", "Candy Kingdom", "Star Miners"]
      }
    },
    {
      "turns": [
        ("im in the car w/o headphones, can i play {game} w the sound off",
         "Totally — turn on captions in settings so you don't miss any dialogue. Mute button is usually top right."),
        ("ok sound off captions on. the captions are tiny",
         "Captions have their own size slider in the same menu. Bump it up and they'll be readable from the moon."),
        ("ohh better. wait, can captions be different colors",
         "They can! Some games let you pick caption color and background. Customization is half the fun."),
        ("pink captions lol. gtg were at the store",
         "Pink captions, the superior choice. See you after the store run.")
      ],
      "slots": {
        "game": ["Dragon Land", "Sky Racers", "Pixel Pets", "Robot Arena", "Jungle Jump", "Snow Forts", "Space Farms", "Wizard World", "Candy Kingdom", "Star Miners"]
      }
    },
    {
      "turns": [
        ("when i play {game} my head gets dizzy like im on a boat 🤢",
         "That happens to lots of players — camera motion does it. Try turning down camera sensitivity and switching off screen shake."),
        ("where is that",
         "Settings, then controls or display depending on the game. Camera sensitivity slider, screen shake toggle."),
        ("found the slider. do i go lower for less dizzy",
         "Yes, lower means calmer camera. Small steps — drop it a bit, play a few minutes, adjust again."),
        ("ok less dizzy already. u kno everything lol",
         "Not everything, but motion cures are in my top ten. Enjoy the calm seas.")
      ],
      "slots": {
        "game": ["Dragon Land", "Sky Racers", "Pixel Pets", "Robot Arena", "Jungle Jump", "Snow Forts", "Space Farms", "Wizard World", "Candy Kingdom", "Star Miners"]
      }
    },
    {
      "turns": [
        ("how do i even get to my {place}?? i clicked everywhere",
         "It's sneaky! Tap your avatar picture in the corner — that opens the menu with the {place} in the list."),
        ("wait which corner",
         "Top left, the little face icon. On some screens it's top right if the layout flipped."),
        ("FOUND IT. omg it was right there the whole time",
         "The classic 'it was right there' moment. Happens to teachers daily, I hear."),
        ("lol ok thx. gtg do the lesson before my teacher notices",
         "Quick and quiet — the ninja way of homework. Good luck.")
      ],
      "slots": {
        "place": ["profile", "backpack", "streak page", "lessons tab", "inventory", "dashboard", "avatar editor", "progress page", "quest log", "settings menu"]
      }
    }
  ]
}

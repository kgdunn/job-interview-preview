# Candidate brief - preview case

This repo is a **preview**. It is not the case you'll be assessed on.

You have it for a week. The real session uses a different repo with the same
structure, the same toolset, and the same format of tickets. You'll get that one
shortly before we start - enough time to build it and skim it, not enough to
study it. It comes with its own brief.

So the point of this preview is to get everything slow out of the way now, and
to know what the hour looks like before you're in it.

## Do this before the day

**1. Get the stack running.** You need Docker; everything else is in the compose
file.

```bash
make up
make seed SCALE=medium     # ~3k batches, a couple of minutes
make test                  # should be green
curl localhost:8000/batches?limit=5
```

If that last command answers, you're ready. Two things that catch people out:

- On a remote box or through a VS Code remote session, forward port **7687**
  (bolt) as well as 7474, or the Neo4j browser loads and then fails to log in.
- `make test` needs the seed to have run. A failure there is usually an empty
  database, not a broken test.

**2. Get your agent tool installed and authenticated** - whichever you use day
to day. We're not prescribing one and not providing one. Model spend is on your
own account: an hour of ordinary use is cheap, a couple of unattended "go fix
everything" runs are not.

**3. Practise on this repo.** Read `README.md`, then work through as many of the
six tickets in `BACKLOG.md` as you like - nothing there is off limits. The real
tickets will be different, but they will look and behave like these.

Because you'll only have the real code briefly, the thing worth practising is
picking up an unfamiliar codebase quickly with your agent - not memorising this
one.

If any of the setup doesn't work, tell us **before** the day. On the day we'd
rather move the session than watch you fight Docker.

## What the hour looks like

The same shape on the real case:

- **A short orientation.** You'll have had the repo briefly. We'll ask what you
  make of it so far, and which tickets you'd pick.
- **Two tickets, around 40 minutes.** One from each group in the backlog - we
  choose, not you. **One will be a code review rather than a build**: you say
  whether you'd merge it, and why. And **a requirement will change partway
  through**. That part is deliberate, and you can't prepare for it.
- **Would you trust this system?** Somebody is going to make a production
  decision on these numbers. If you wouldn't, what exactly is wrong, how did you
  establish it, and what would you do about it?

If a ticket seems wrong to you, say so. We'd much rather hear that than watch
you implement something you think is a bad idea - sometimes that is the right
answer.

Commit as you go, with messages you'd be happy for a colleague to read.

## What we're assessing

Roughly in order of weight:

1. **Judgement** - what you work on, what you leave, and whether you can explain
   both.
2. **Verification** - whether you checked that things do what you believe,
   rather than accepting output that looks plausible.
3. **Use of the agent** - whether you gave it enough context to be useful, and
   whether you checked what it handed back.
4. **Communication** - explaining a problem to someone who hasn't read the code.

Writing lots of code isn't the goal. One real fix, one well-argued piece of
pushback, and a clear account of what else is wrong is a strong hour. Two
tickets finished and neither of them checked is a weaker one.

## Practical

- Share your screen and think out loud. We'll mostly stay quiet, but ask us
  anything - we're playing the team that wrote this.
- Anything outside the two chosen tickets is off the menu. If you think
  something else matters more, say so - don't go and do it instead.
- No expectation that you finish. There is an expectation you can say what you'd
  do next.

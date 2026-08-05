# Candidate brief

One hour, live, on a codebase you have in advance. It is not a quiz. We want to
see how you work with an agentic coding tool in the loop, and whether you can
defend what you did.

**This is a preview case.** The real session runs the same way on a case like
this one - same tooling, same setup, same shape of tasks. Whatever you get
working now carries over, so the hour isn't spent on install problems.

Please read this before the day.

## Before the session

Have the stack **up and running before we start**. You need Docker; everything
else is in the compose file.

```bash
make up
make seed SCALE=medium     # ~3k batches, a couple of minutes
make test                  # should be green
curl localhost:8000/batches?limit=5
```

If that last command answers, you're ready.

Two things that have caught people out:

- On a remote box or through a VS Code remote session, forward port **7687**
  (bolt) as well as 7474. Otherwise the Neo4j browser loads fine and then fails
  to log in.
- `make test` needs the seed to have run. A failure there is usually an empty
  database, not a broken test.

Have your **agent tool installed and authenticated** too - whichever you use day
to day. We're not prescribing one and not providing one. Model spend is on your
own account: an hour of ordinary use is cheap, a couple of unattended "go fix
everything" runs are not.

If any of this doesn't work, tell us **before** the day. On the day we'd rather
move the session than watch you fight Docker.

## The system

`batchwatch` monitors batch fermentation across four manufacturing sites. Read
`README.md` - what it does, how to run it, and what the team already knows is
rough.

## The hour

**Prepare as much as you like. We assume you have.** Read it, run it, break it,
point your agent at it. Nobody gets credit for arriving cold.

- **5 min** - what you found while preparing, and which two tickets you'd have
  picked. Then we tell you which two you're actually doing.
- **40 min** - two tickets, one from each group in `BACKLOG.md`. FERM-130 is a
  review rather than a build: say whether you'd merge it and why. **A
  requirement will change partway through** - that's the part you can't prepare
  for, and it's deliberate.
- **15 min** - would you trust this system? Somebody is going to make a
  production decision on these numbers. If you wouldn't, what exactly is wrong,
  how did you establish it, and what would you do about it?

If a ticket seems wrong to you, say so. We'd much rather hear that than watch
you implement something you think is a bad idea - on one of these it may be the
right answer.

Commit as you go, with messages you'd be happy for a colleague to read.

## What we're assessing

Roughly in order of weight:

1. **Judgement** - what you'd work on, what you'd leave, and whether you can
   explain both.
2. **Verification** - whether you checked that things do what you believe,
   rather than accepting output that looks plausible. If you prepared an answer,
   we'll ask how you know it's right.
3. **Use of the agent** - whether you gave it enough context to be useful, and
   whether you checked what it handed back.
4. **Communication** - explaining a problem to someone who hasn't read the code.

Writing lots of code isn't the goal. One real fix, one well-argued piece of
pushback, and a clear account of what else is wrong is a strong hour. Two
tickets finished and neither of them checked is a weaker one.

## Practical

- Share your screen and think out loud. We'll mostly stay quiet, but ask us
  anything - we're playing the team that wrote this.
- Prepared notes and branches are fine. Just tell us what's prepared and what's
  live; we'll find out either way, and volunteering it costs you nothing.
- Anything outside the two groups in `BACKLOG.md` is off the menu, including the
  lint backlog. If you think a parked ticket matters more, say so - don't go and
  do it instead.
- No expectation that you finish. There is an expectation you can say what you'd
  do next.

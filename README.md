# Permit Finder

A docker container to help find avaliable permits for [Recreation.gov](http://recreation.gov) locations (largely rivers).

## Configuration

As with most programs that allow the user to have some preferences, this one requires some information to run.

We will need to give it some info to send email, and more importantly tell it what rivers we want permits for.

### Environment variables

It takes several environment variables to configure email.

`SMTP_SERVER`, `SMTP_PORT`, `SMTP_EMAIL_ADDRESS`, `SMTP_PASSWORD`, `EMAIL_TO`, `YAML_PATH`

If you are going to use gmail to send from, those might be

```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL_ADDRESS=you@gmail.com
SMTP_PASSWORD=your_password
EMAIL_TO=your_other_address@server.com
```

(If you are using Gmail remember to [allow "less secure apps"](https://www.google.com/settings/security/lesssecureapps))

`YAML_PATH` is for when your permit wish list yaml is located at somewhere other than `/permits.yaml`.

### Permits wanted

Now for the more fun selection, what permits do you want to snag, for how many people, and when.

The script reads a yaml file in the form of:

```yaml
permits:
- section: 1782381139
  start: 7/1/2017
  end: 8/1/2017
  group_size: 8
- section: 523907650
  start: 6/1/2017
  end: 8/1/2017
  group_size: 8
- section: 523907650
  start: 9/1/2017
  end: 10/1/2017
  group_size: 4
- section: 523907650
  start: 1/1/2017
  end: 4/1/2017
  group_size: 4
```

You may think 'oh god what do those numbers correspond to', well Recreation.gov has a `permit_type_id` for every location that is on the site. Thankfully I have a handy list below for those of you who don't want to poke into the code (`permit_finder/recreation_helpers.py`).

Each permit wanted needs a few basic pieces of info: The `permit_type_id`, the start date, end date, and the maximum number on the permit to search for. Take the `permit_type_id` and place it as the section value, and the rest should be self explanitory. (dates need to be in m/d/yyyy format).

So if I wanted to have it search for a permit for the Middle Fork of the Salmon (`permit_type_id` of 523879550) between July 1st and August 3rd for 5 people I would make an entry into the yaml. First I start with `permits:` to show that I have a list of permits that I want (even if I'm only searching for one).

```yaml
permits:
- section: 523879550
  start: 7/1/2017
  end: 8/3/2017
  group_size: 5
```

Note how each requested permit starts with `-` and then the other parts of it's information is spaced in to match `section`. That's how it knows it's all one part.

Now if I wanted a Selway (523888682) during the same period for the same group I would add another section:

```yaml
permits:
- section: 523879550 # Middle Fork Salmon
  start: 7/1/2017
  end: 8/3/2017
  group_size: 5
- section: 523888682 # Selway
  start: 7/1/2017
  end: 8/3/2017
  group_size: 5
```

Note: Anything after the number sign `#` gets ignored, so you can mark notes in your permit wish list file appropriately!

## List of sections and permit_type_id

- Desolation/Gray (Green River) - 1267601734
- Gates of Lodore - Green River - 2102427966
- Hells Canyon - 523907650
- Main Salmon - 523898830
- Middle Fork Salmon - 523879550
- Rogue - 2260300985
- San Juan - Mexican Hat to Clay Hill - 1782381139
- San Juan - Montezuma Creek to Sand Island - 1782408111
- San Juan - Sand Island to Clay Hills - 1782381178
- San Juan - Sand Island to Mexican Hat - 1782381178
- Selway - 523888682
- Yampa - Deerlodge Park - 2102428458

## Running with Docker Compose

The easiest way to run it is with [Docker](https://www.docker.com/community-edition) Compose on your own machine. Change the `permits.yaml` and create a `common.env` with your email information in the same folder.

`common.env`
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL_ADDRESS=you@gmail.com
SMTP_PASSWORD=your_password
EMAIL_TO=your_other_address@server.com
```

Then you can run a command in that folder in your terminal to run it.

```
docker-compose up --build
```

## Running with Kubernetes

The much awesomer (definately a word) way is to run it on a Kubernetes cluster. I'm not going to go into specifics, but it's awesome.
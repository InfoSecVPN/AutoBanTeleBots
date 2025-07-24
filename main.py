import asyncio
from telethon import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest, EditBannedRequest
from telethon.tl.types import PeerChannel, PeerUser, ChatBannedRights


# this script bans all members from your telegram channel that do not have a public profile picture, on loop.


api_id = 123456789
api_hash = 'secret hash here'
channel_identifier = '@InfoSecVPN' # Your telegram channel username here

kick_rights = ChatBannedRights(
    until_date=None,
    view_messages=True
)

KICK_DELAY = 1.5
MAX_KICKS_PER_BATCH = 20
BATCH_COOLDOWN = 30
LOOP_COOLDOWN = 30

async def kick_no_pfp():
    while True:
        if isinstance(channel_identifier, int):
            channel = await client.get_entity(PeerChannel(channel_identifier))
        else:
            channel = await client.get_entity(channel_identifier)

        # gets the channel bio
        full = await client(GetFullChannelRequest(channel))
        channel_bio = full.full_chat.about or "[No Channel Bio]"

        print(f"Channel Title: {channel.title}")
        print(f"Channel Bio: {channel_bio}\n")

        members_to_kick = []
        print("Members without profile pictures:\n")
        async for member in client.iter_participants(channel):
            if not member.photo:
                full_name = (member.first_name or "") + " " + (member.last_name or "")
                full_name = full_name.strip() or "[No Name]"
                print(f"ID: {member.id} | Name: {full_name}")
                members_to_kick.append((member.id, full_name))

        print(f"\nFound {len(members_to_kick)} members without profile pictures.")

        if not members_to_kick:
            print(f"No members to kick. Waiting {LOOP_COOLDOWN} seconds before retrying.")
            await asyncio.sleep(LOOP_COOLDOWN)
            continue

        print("\nStarting to kick members without profile pictures...\n")
        count = 0
        for member_id, full_name in members_to_kick:
            try:
                await client(EditBannedRequest(channel, PeerUser(member_id), kick_rights))
                print(f"Kicked {member_id} ({full_name}) - no PFP.")
                count += 1
                await asyncio.sleep(KICK_DELAY)

                if count % MAX_KICKS_PER_BATCH == 0:
                    print(f"Cooldown after {count} kicks. Waiting {BATCH_COOLDOWN} seconds.")
                    await asyncio.sleep(BATCH_COOLDOWN)

            except Exception as e:
                print(f"Failed to kick {member_id}: {e}")

        print("\nFinished kicking all members without profile pictures.")
        print(f"Waiting {LOOP_COOLDOWN} seconds before next scan.\n")
        await asyncio.sleep(LOOP_COOLDOWN)


with TelegramClient('kick_no_pfp', api_id, api_hash) as client:
    client.loop.run_until_complete(kick_no_pfp())

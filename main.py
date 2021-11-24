import discord
import os
import asyncio
import dotenv

my_product_list = [
    "MLTX3LL/A",  # iPhone 13 Pro 256GB Silver
    "MLU33LL/A",  # iPhone 13 Pro 512GB Silver
    "MLUA3LL/A",  # iPhone 13 Pro 1TB Silver
    "MLTW3LL/A",  # iPhone 13 Pro 256GB Graphite
    "MLU13LL/A",  # iPhone 13 Pro 512GB Graphite
    "MLU93LL/A",  # iPhone 13 Pro 1TB Graphite
    "MLU03LL/A",  # iPhone 13 Pro 256GB Sierra Blue
    "MLU73LL/A",  # iPhone 13 Pro 512GB Sierra Blue
    "MLUD3LL/A",  # iPhone 13 Pro 1TB Sierra Blue
    "MLKV3LL/A",  # iPhone 13 Pro Max 256GB Sierra Blue
    "MLL03LL/A",  # iPhone 13 Pro Max 512GB Sierra Blue
    "MLL53LL/A",  # iPhone 13 Pro Max 1TB Sierra Blue
    "MLKT3LL/A",  # iPhone 13 Pro Max 256GB Silver
    "MLKX3LL/A",  # iPhone 13 Pro Max 512GB Silver
    "MLL33LL/A",  # iPhone 13 Pro Max 1TB Silver
    "MLKR3LL/A",  # iPhone 13 Pro Max 256GB Graphite
    "MLKW3LL/A",  # iPhone 13 Pro Max 512GB Graphite
    "MLL23LL/A",  # iPhone 13 Pro Max 1TB Graphite
]

# initial setup
dotenv.load_dotenv()
client = discord.Client()
debug = False

execute_interval = int(os.getenv("EXECUTE_INTERVAL")) * 60


async def background_task(function, interval):
    await client.wait_until_ready()
    while not client.is_closed():
        await function()
        await asyncio.sleep(interval)


async def print_and_send(message):
    channel_id = int(os.getenv("CHANNEL_ID"))
    channel = client.get_channel(channel_id)
    await channel.send(message)
    if debug:
        print(message)
        print(channel_id)
        print(channel)


@client.event
async def on_ready():
    print(f"Bot is now running. I am {client.user}.")


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.lower().startswith("!ping"):
        # send back pong with current time and server data
        # message author timezone
        await message.channel.send(
            f"pong! {message.author.mention}"
            + "\nTime: "
            + str(message.created_at)
            + "\nChannel ID: "
            + str(message.channel.id)
            + "\nGuild: "
            + str(message.guild.name)
            + "\n("
            + str(message.guild.id)
            + ")"
        )
        # current channel id

    if message.content.lower().startswith("!stock"):
        await send_apple_stock()


async def send_apple_stock(
    product_id=my_product_list,
    location_zip=os.getenv("LOCATION_ZIP"),
    distance=100,
):
    """
    send the stock of a product at a given location.
    """
    # use query string to get stock
    BASE_URL = "https://www.apple.com/shop/retail/pickup-message?"
    counter = 0

    DEVICE_STRING = ""
    for product in product_id:
        DEVICE_STRING += f"parts.{counter}={product}&"
        counter += 1

    LOCATION_STRING = f"location={location_zip}"
    url = BASE_URL + DEVICE_STRING + LOCATION_STRING

    # json response
    import requests

    response = requests.get(url).json()
    if response["head"].get("status") != "200":
        # send error message to discord channel
        await print_and_send(f"Error: {response['head']['status']}")
    else:
        # purify response
        final_response = []
        discord_payload = []
        body = response["body"]
        for store in body["stores"]:
            if int(store["storedistance"]) <= distance:
                store_data = store["partsAvailability"]
                # traverse key value
                for key, value in store_data.items():
                    discord_payload.append(
                        value["storePickupProductTitle"]
                        + "\n"
                        + value["storePickupQuote"]
                    )
                final_response.extend(discord_payload)
                discord_payload = []
        something_is_available = False
        for product in final_response:
            if "today" in product.lower():
                await print_and_send(product)
                something_is_available = True
        if not something_is_available:
            await print_and_send("**No stock available.**")


def main():
    client.loop.create_task(background_task(send_apple_stock, execute_interval))
    client.run(os.getenv("TOKEN"))


if __name__ == "__main__":
    main()

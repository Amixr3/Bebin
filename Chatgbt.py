from rubpy import Message, Client, handlers, models, methods
from asyncio import run, sleep , gather , ensure_future , create_task
import random, aiohttp
from datetime import datetime
import requests

my_group = "g0DW8K700aaa4d5290f5da721a979af8"
my_filters = ("@", "join", "rubika.ir")
group_admins = []


silence_list = []
no_gifs = False
warning_users = []
warns_del = 3
channe_id = "@create_bot"
my_insults = (
    "کیر",
    "کص",
    "کون",
    "کس ننت",
    "کوس",
    "کوص",
    "ممه",
    "ننت",
    "بی ناموس",
    "بیناموس",
    "بیناموص",
    "بی ناموص",
    "گایید",
    "جنده",
    "جندع",
    "جیندا",
    "پستون",
    "کسکش",
    "ننه کس",
    "اوبی",
    "هرزه",
    "قحبه",
    "عنتر",
    "فاک",
    "کسعمت",
    "کصخل",
    "کسخل",
    "تخمی",
    "سکس",
    "صکص",
    "کسخول",
    "کسشر",
    "کسشعر",
)


texts_bot = [
    "بنال",
    "چیه بدبخت",
    "باز اومد",
    "هعی",
    "هن",
    "بگیر بخواب",
    "بله",
    "بلههه",
    "جانم",
    "جونم",
    "بگو",
    "خستم کردی",
    "بسه دیگه",
]


async def Time_New():
    now = datetime.now()
    return now.strftime("%H:%M:%S")


def getAds(string: str) -> bool:
    string = string.lower()
    for filter in my_filters:
        if filter in string:
            return True
        else:
            continue
    return False


def getInsults(string: str) -> bool:
    for filter in my_insults:
        if filter in string:
            return True
        else:
            continue
    return False


async def deleteMessage(client: Client, message_ids: str):
    await sleep(5)
    await client.delete_messages(my_group, message_ids)


async def updateAdmins(client: Client) -> None:
    global group_admins
    results = await client(methods.groups.GetGroupAdminMembers(my_group))
    results = results.to_dict().get("in_chat_members")
    for result in results:
        GUID = result.get("member_guid")
        if not GUID in group_admins:
            group_admins.append(GUID)
        else:
            continue


async def get_user_name(client: Client, guid: str):
    user_info = await client.get_user_info(guid)
    return user_info.user.first_name


async def warn_user(client: Client, guid: str):
    num_warns = 0
    for warn in warning_users:
        if warn == guid:
            num_warns += 1
    name_user = await get_user_name(client, guid)
    if num_warns < warns_del:
        message_id = await client.send_message(
            my_group,
            f"👤 کاربر [{name_user}]({guid}) شما یک اخطار دریافت کردید\n\n- تعداد اخطار : {num_warns} از {warns_del} میباشد \n\n⚠️ مواظب باشید اخراج نشید",
        )
    elif num_warns >= warns_del:
        message_id = await client.send_message(
            my_group,
            f"👤 کاربر [{name_user}]({guid}) شما یک اخطار دریافت کردید\n\n- تعداد اخطار : {num_warns} از {warns_del} میباشد \n\n⚠️ شما حذف خواهید شد",
        )
        await client.ban_group_member(my_group, guid)
    await deleteMessage(client, [message_id.message_update.message_id])


async def get_guid_by_message_id(client: Client, mesage_id: str):
    messages = await client.get_messages_by_ID(my_group, [mesage_id])
    return messages.messages[0].author_object_guid


async def unwarnUser(guid: str):
    for guid_user in warning_users:
        if guid_user == guid:
            warning_users.remove(guid_user)


async def start_bot(client: Client):
    await updateAdmins(client)
    name_gap = await client.get_group_info(my_group)
    name_gap = name_gap.group.group_title
    await client.send_message(
        my_group,
        f"ربات [ {name_gap} ] با موفقیت فعال شد 🌸 \n\nبرای نمایش دستورات ربات دستور زیر را ارسال کنید \n `!info `\n\n- Time 『 {await Time_New()} 』",
    )


async def select_bestUser(client: Client, replay: str):
    meembers_gap = await client.get_group_all_members(my_group)
    meembers_gap = meembers_gap.in_chat_members
    member = meembers_gap[random.randint(0, len(meembers_gap) - 1)]
    member = await client.get_user_info(member.member_guid)
    member = member.user.to_dict()
    if "username" in member:
        message_id = await client.send_message(
            my_group, f"اینه @{member['username']} 😂", replay
        )
    else:
        message_id = await client.send_message(
            my_group, f"اینه [{member['first_name']}]({member['user_guid']}) 😂 ", replay
        )
    await deleteMessage(client, [message_id.message_update.message_id])


async def make_request():
    url = "https://api.codebazan.ir/bio/"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()


async def target(my_array, i: int, client: Client):
    await client.delete_messages(my_group, my_array[i : i + 30])


async def deleteMessages(client: Client, replay_message: str):
    try:
        messages_ids = []
        messages = await client.get_messages_interval(my_group, replay_message)
        while messages.old_has_continue:
            messages = await client.get_messages_interval(
                my_group, messages.old_max_id
            )
            for messeaged in messages.messages:
                messages_ids.append(messeaged.message_id)
        for i in range(0, len(messages_ids), 30):
            tasks = []
            task = ensure_future(target(messages_ids, i, client))
            tasks.append(task)
        await gather(*tasks)
        message_id = await client.send_message(
            my_group,
            f"تعداد {str(len(messages_ids))} پیام پاک شد !",
            replay_message,
        )
    except:
        message_id = await client.send_message(
            my_group,
            f"تعداد {str(len(messages_ids))} پیام پاک شد !",
            replay_message,
        )
        

def ChatGPT_tap30(prompt: str) -> dict:
    requests.session().cookies.clear()
    options_url = "https://api.tapsi.cab/api/v1/chat-gpt/chat/completion"
    headers = {
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type,x-agent",
        "Origin": "https://chatgpt.tapsi.cab",
    }
    requests.options(options_url, headers=headers)
    ip_address = "5.121.39.59"
    ip_parts = ip_address.split(".")
    random.shuffle(ip_parts)
    new_ip = ".".join(ip_parts)
    webkit_version = f"{random.randint(500, 600)}.{random.randint(0, 99)}"
    major_version = random.randint(100, 200)
    minor_version = random.randint(0, 9)
    build_version = random.randint(0, 9999)
    safari_version = f"{random.randint(500, 600)}.{random.randint(0, 99)}"
    user_agent = f"Mozilla/5.0 (Linux; Android 10; STK-L21) AppleWebKit/{webkit_version} (KHTML, like Gecko) Chrome/{major_version}.0.{minor_version}.{build_version} Mobile Safari/{safari_version}"
    post_url = "https://api.tapsi.cab/api/v1/chat-gpt/chat/completion"
    headers = {
        "Content-Type": "application/json",
        "X-Agent": user_agent,
        "X-Forwarded-For": new_ip,
        "Origin": "https://chatgpt.tapsi.cab",
    }
    data = {"messages": [{"role": "user", "content": prompt}]}
    try:
        return requests.post(post_url, headers=headers, json=data).json()
    except:
        return dict(result=False)


async def SendResultChatGPT(text: str, message: Message) -> None:
    await sleep(2)
    result = ChatGPT_tap30(text)
    if result["result"] != None:
        await message.reply(result["data"]["message"]["content"])
    else:
        await message.reply("خطا، لطفا مجدد امتحان کنید.")


async def main():
    async with Client(session="bot") as client:
        await start_bot(client)

        @client.on(handlers.MessageUpdates(models.is_group()))
        async def updates(update: Message):
            if update.object_guid == my_group:
                if (
                    not update.author_guid in group_admins
                    and "forwarded_from" in update.to_dict().get("message").keys()
                ):
                    guid = await get_guid_by_message_id(client, update.message_id)
                    await update.delete_messages()
                    warning_users.append(guid)
                    await warn_user(
                        client,
                        guid,
                    )

                if update.raw_text != None:
                    if not update.author_guid in group_admins and getAds(
                        update.raw_text
                    ):
                        guid = await get_guid_by_message_id(client, update.message_id)
                        await update.delete_messages()
                        warning_users.append(guid)
                        await warn_user(
                            client,
                            guid,
                        )

                    elif update.raw_text == "ربات" or update.raw_text == "bot":
                        await update.reply(texts_bot[random.randint(0, len(texts_bot))])

                    elif getInsults(update.raw_text):
                        message_id = await update.reply(
                            f"یک پیام مستهجن حذف شد \n\n- Time : {await Time_New()}"
                        )
                        await update.delete_messages()
                        await deleteMessage(
                            client, [message_id.message_update.message_id]
                        )

                    elif (
                        update.author_guid in group_admins
                        and update.raw_text == "!open"
                    ):
                        result = await client(
                            methods.groups.SetGroupDefaultAccess(
                                my_group, ["SendMessages"]
                            )
                        )
                        message_id = await update.reply(
                            f"گروه باز شد.\n\n- Time : {await Time_New()}"
                        )
                        await deleteMessage(
                            client,
                            [update.message_id, message_id.message_update.message_id],
                        )

                    elif (
                        update.author_guid in group_admins
                        and update.raw_text == "!close"
                    ):
                        result = await client(
                            methods.groups.SetGroupDefaultAccess(my_group, [])
                        )
                        message_id = await update.reply(
                            f"گروه بسته شد.\n\n- Time : {await Time_New()}"
                        )
                        await deleteMessage(
                            client,
                            [update.message_id, message_id.message_update.message_id],
                        )

                    elif (
                        update.author_guid in group_admins
                        and update.raw_text == "!warn"
                        and update.reply_message_id != None
                    ):
                        guid = await get_guid_by_message_id(
                            client, update.reply_message_id
                        )
                        if not guid in group_admins:
                            warning_users.append(guid)
                            await warn_user(
                                client,
                                guid,
                            )
                            await deleteMessage(client, [update.message_id])
                        else:
                            message_id = await reply("کاربر ادمین میباشد")
                            await deleteMessage(
                                client,
                                [
                                    update.message_id,
                                    message_id.message_update.message_id,
                                ],
                            )

                    elif update.author_guid in group_admins and update.text.startswith(
                        "!unwarn @"
                    ):
                        username = update.text.split("@")[-1]
                        user_info = await client.get_object_by_username(username)
                        user_info = user_info.user.user_guid
                        if not user_info in group_admins:
                            if user_info in warning_users:
                                await unwarnUser(user_info)
                                name_user = await get_user_name(client, user_info)
                                message_id = await client.send_message(
                                    my_group,
                                    f"کاربر [{name_user}]({user_info}) اخطار های شما پاک شدند \n\n- Time : {await Time_New()}",
                                )
                            else:
                                message_id = await update.reply(
                                    "کاربر اخطاری ندارد که پاک شود"
                                )
                        else:
                            message_id = await update.reply(
                                "کاربر در گروه ادمین میباشد"
                            )
                        await deleteMessage(
                            client,
                            [update.message_id, message_id.message_update.message_id],
                        )

                    elif (
                        update.author_guid in group_admins
                        and update.raw_text == "!look-gif"
                    ):
                        global no_gifs
                        no_gifs = True
                        message_id = await update.reply(
                            f"گیف قفل شد.\n\n- Time : {await Time_New()}"
                        )
                        await deleteMessage(
                            client,
                            [update.message_id, message_id.message_update.message_id],
                        )

                    elif (
                        update.author_guid in group_admins
                        and update.raw_text == "!unlook-gif"
                    ):
                        no_gifs = False
                        message_id = await update.reply(
                            f"قفل گیف رفع شد.\n\n- Time : {await Time_New()}"
                        )
                        await deleteMessage(
                            client,
                            [update.message_id, message_id.message_update.message_id],
                        )

                    elif update.raw_text == "اسکل گپ کیه":
                        await select_bestUser(client, update.message_id)
                        await deleteMessage(client, [update.message_id])

                    elif (
                        update.author_guid in group_admins
                        and update.raw_text.startswith("!silent")
                    ):
                        if update.reply_message_id != None:
                            try:
                                result = await client(
                                    methods.messages.GetMessagesByID(
                                        my_group, [update.reply_message_id]
                                    )
                                )
                                result = result.to_dict().get("messages")[0]
                                if not result.get("author_object_guid") in group_admins:
                                    global silence_list
                                    silence_list.append(
                                        result.get("author_object_guid")
                                    )
                                    message_id = await update.reply(
                                        f"کاربر مورد نظر در حالت سکوت قرار گرفت.\n\n- Time : {await Time_New()}"
                                    )
                                else:
                                    message_id = await update.reply(
                                        "کاربر مورد نظر در گروه ادمین است."
                                    )
                                await deleteMessage(
                                    client,
                                    [
                                        update.message_id,
                                        message_id.message_update.message_id,
                                    ],
                                )
                            except IndexError:
                                message_id = await update.reply(
                                    "ظاهرا پیامی که روی آن ریپلای کرده اید پاک شده است."
                                )
                                await deleteMessage(
                                    client,
                                    [
                                        update.message_id,
                                        message_id.message_update.message_id,
                                    ],
                                )

                        elif update.text.startswith("!silent @"):
                            username = update.text.split("@")[-1]
                            if username != "":
                                result = await client(
                                    methods.extras.GetObjectByUsername(username.lower())
                                )
                                result = result.to_dict()
                                if result.get("exist"):
                                    if result.get("type") == "User":
                                        user_guid = result.get("user").get("user_guid")
                                        if not user_guid in group_admins:
                                            silence_list.append(user_guid)
                                            message_id = await update.reply(
                                                f"کاربر مورد نظر در حالت سکوت قرار گرفت.\n\n- Time : {await Time_New()}"
                                            )
                                        else:
                                            message_id = await update.reply(
                                                "کاربر مورد نظر در گروه ادمین است."
                                            )
                                    else:
                                        message_id = await update.reply(
                                            "کاربر مورد نظر کاربر عادی نیست."
                                        )
                                else:
                                    message_id = await update.reply(
                                        "آیدی مورد نظر اشتباه است."
                                    )
                            else:
                                message_id = await update.reply(
                                    "آیدی مورد نظر اشتباه است."
                                )
                            await deleteMessage(
                                client,
                                [
                                    update.message_id,
                                    message_id.message_update.message_id,
                                ],
                            )
                        else:
                            message_id = await update.reply(
                                "روی یک کاربر ریپلای بزنید."
                            )
                            await deleteMessage(
                                client,
                                [
                                    update.message_id,
                                    message_id.message_update.message_id,
                                ],
                            )

                    elif update.author_guid in group_admins and update.text.startswith(
                        "!add @"
                    ):
                        username = update.text.split("!add @")[-1]
                        result = await client.get_object_by_username(username)
                        if result.exist == True:
                            try:
                                await client.add_group_members(
                                    my_group, member_guids=[result.user.user_guid]
                                )
                            except:
                                await update.reply("خطا در افزودن کاربر !")
                        else:
                            message_id = await update.reply("آیدی مورد نظر اشتباه است.")

                    elif (
                        update.author_guid in group_admins
                        and update.reply_message_id != None
                        and update.raw_text == "!pin"
                    ):
                        await update.pin(my_group, update.reply_message_id)
                        await update.reply(
                            f"پیام با موفقیت سنجاقک شد \n\n- Time : {await Time_New()}"
                        )

                    elif (
                        update.author_guid in group_admins
                        and update.raw_text.startswith("!clean-silent @")
                    ):
                        username = update.text.split("!clean-silent @")[-1]
                        result = await client.get_object_by_username(username)
                        if result.exist == True:
                            if result.user.user_guid in silence_list:
                                silence_list.remove(result.user.user_guid)
                                message_id = await update.reply(
                                    "کاربر با موفقیت از لیست افراد درحال سکوت بیرون امد"
                                )
                            else:
                                message_id = await update.reply(
                                    "کاربر در لیست افراد درحال سکوت وجود ندارد !"
                                )
                        else:
                            message_id = await update.reply("آیدی مورد نظر اشتباه است.")
                    elif (
                        update.author_guid in group_admins
                        and update.raw_text.startswith("!clean-list-silent")
                    ):
                        if silence_list == []:
                            message_id = await update.reply("لیست سکوت خالی است.")
                        else:
                            silence_list = []
                            message_id = await update.reply("لیست سکوت خالی شد.")
                        await deleteMessage(
                            client,
                            [update.message_id, message_id.message_update.message_id],
                        )

                    elif update.raw_text == "!time":
                        await update.reply(f"➲ Time 『 {await Time_New()} 』")

                    elif update.raw_text == "!bio":
                        text_bio = await make_request()
                        await update.reply(text_bio)

                    elif update.raw_text.startswith("//"):
                        text: str = update.raw_text.strip().replace("// ", "")
                        await update.reply(
                            "درخواست شما با موفقیت ثبت شد. لطفا چند لحظه صبر کنید . . ."
                        )
                        create_task(SendResultChatGPT(text, update))
                    
                    elif update.raw_text == "!link":
                        result = await client(methods.groups.GetGroupLink(my_group))
                        result = result.to_dict().get("join_link")
                        message_id = await update.reply(
                            f"لینک گروه: {result}\n\n- Time : {await Time_New()}"
                        )
                        await deleteMessage(
                            client,
                            [update.message_id, message_id.message_update.message_id],
                        )
                        
                    elif (
                        update.author_guid in group_admins
                        and update.text == "!clean-gap"
                    ):
                        await deleteMessages(client , update.message_id)

                    elif (
                        update.author_guid in group_admins
                        and update.text == "!update-admins"
                    ):
                        message_ids = update.message_id
                        reply = await update.reply(
                            "در حال به روزرسانی لیست ادمین ها..."
                        )
                        await updateAdmins(client)
                        await sleep(2)
                        message_id = await reply.edit(
                            f"به روزرسانی لیست ادمین ها انجام شد.\n\n- Time : {await Time_New()}"
                        )
                        await deleteMessage(
                            client, [message_ids, message_id.message_update.message_id]
                        )

                    elif (
                        update.author_guid in group_admins
                        and update.raw_text == "!info"
                    ):
                        text = f"""🖇 رهنمای ربات


⚙ `!ban ` 
- حذف شخص از گپ [حتما رپلای کنید]

⚙ `!ban @id `
- حذف شخص از گپ

⚙ `!warn ` 
- اخطار به شخص [حتما رپلای کنید]

⚙ `!unwarn @id `
- حذف اخطار شخص

⚙ `!silent ` 
- حذف پیام های شخص در گپ

⚙ `!silent @id `
- حذف پیام های شخص در گپ

⚙ `!clean-silent @id `
بیرون اوردن شخص از لیست افراد درحال سکوت

⚙ `!clean-list-silent`
- پاکسازی لیست سکوت

⚙ `!update-admins `
- اپدیت مدیران

⚙ `!look-gif `
- حذف گیف در گروه

⚙ `!unlook-gif `
- پاک نشدن گیف در گروه توسط ربات

⚙ `!open `
- بازکردن گروه

⚙ `!close `
- قفل گروه

⚙ `!pin `
پین کردن پیام

⚙ `اس.کل گپ کیه `
بدبخت کردن یک عضو گپ😂

⚙ `!add @id  `
افزودن عضو با یوزرنیم

⚙ `!clean-gap  `
پاکسازی پیام های گروه

⚙ `//`
پرسیدن سوال از هوش مصنوعی

⚙ `!time  `
نمایش ساعت 

⚙ `!bio  `
ارسال بیوگرافی به گروه

───> channel : {channe_id} <───

🤖 قابلیت های خودکار

⚙ ضدلینک
- حذف لینک های ارسالی به گروه

⚙ حذف فش
- حذف فش های ارسالی به گروه

- Time : {await Time_New()}"""
                        await update.reply(text)

                    elif update.author_guid in group_admins and update.text.startswith(
                        "!ban"
                    ):
                        if update.reply_message_id != None:
                            try:
                                result = await client(
                                    methods.messages.GetMessagesByID(
                                        my_group, [update.reply_message_id]
                                    )
                                )
                                result = result.to_dict().get("messages")[0]
                                if not result.get("author_object_guid") in group_admins:
                                    result = await client(
                                        methods.groups.BanGroupMember(
                                            my_group,
                                            result.get("author_object_guid"),
                                        )
                                    )
                                    message_id = await update.reply(
                                        f"کاربر مورد نظر از گروه حذف شد.\n\n- Time : {await Time_New()}"
                                    )
                                else:
                                    message_id = await update.reply(
                                        "کاربر مورد نظر در گروه ادمین است."
                                    )
                                    await deleteMessage(
                                        client,
                                        [
                                            update.message_id,
                                            message_id.message_update.message_id,
                                        ],
                                    )
                            except IndexError:
                                message_id = await update.reply(
                                    "ظاهرا پیامی که روی آن ریپلای کرده اید پاک شده است."
                                )  # created by shayan heidari | rubpy || edited by hadi rostami😂
                                await deleteMessage(
                                    client,
                                    [
                                        update.message_id,
                                        message_id.message_update.message_id,
                                    ],
                                )
                        elif update.text.startswith("!ban @"):
                            username = update.text.split("@")[-1]
                            if username != "":
                                result = await client(
                                    methods.extras.GetObjectByUsername(username.lower())
                                )
                                result = result.to_dict()
                                if result.get("exist"):
                                    if result.get("type") == "User":
                                        user_guid = result.get("user").get("user_guid")
                                        if not user_guid in group_admins:
                                            result = await client(
                                                methods.groups.BanGroupMember(
                                                    my_group, user_guid
                                                )
                                            )
                                            message_id = await update.reply(
                                                f"کاربر مورد نظر از گروه حذف شد.\n\n- Time : {await Time_New()}"
                                            )
                                        else:
                                            message_id = await update.reply(
                                                "کاربر مورد نظر در گروه ادمین است."
                                            )
                                    else:
                                        message_id = await update.reply(
                                            "کاربر مورد نظر کاربر عادی نیست."
                                        )
                                else:
                                    message_id = await update.reply(
                                        "آیدی مورد نظر اشتباه است."
                                    )
                            else:
                                message_id = await update.reply(
                                    "آیدی مورد نظر اشتباه است."
                                )
                        else:
                            message_id = await update.reply(
                                "روی یک کاربر ریپلای بزنید."
                            )  # created by shayan heidari | rubpy || edited by hadi rostami😂
                        await deleteMessage(
                            client,
                            [update.message_id, message_id.message_update.message_id],
                        )

        @client.on(handlers.MessageUpdates(models.is_group()))
        async def updates(update):
            if update.object_guid == my_group:
                if update.author_guid in silence_list:
                    await update.delete_messages()
                else:
                    if no_gifs:
                        if not update.author_guid in group_admins:
                            result = await client(
                                methods.messages.GetMessagesByID(
                                    my_group, [update.message_id]
                                )
                            )
                            result = result.to_dict().get("messages")[0]
                            if (
                                result.get("type") == "FileInline"
                                and result.get("file_inline").get("type") == "Gif"
                            ):
                                await update.delete_messages()  # created by shayan heidari | rubpy || edited by hadi rostami😂

        await client.run_until_disconnected()


run(main())

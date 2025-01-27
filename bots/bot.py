from botbuilder.core import ActivityHandler, ConversationState, UserState, TurnContext
from botbuilder.core.teams import TeamsActivityHandler
from botbuilder.dialogs import Dialog
from botbuilder.schema import ChannelAccount, Attachment, Activity, ActivityTypes
# from botbuilder.schema.teams import TabSubmit, TabRequest, TaskModuleRequest, TaskModuleResponse
from typing import List
from helpers.dialog_helper import DialogHelper
from helpers.activity_helper import create_welcome_activity
from .ConversationData import ConversationData
from views import *
import traceback


class Bot(ActivityHandler):
    def __init__(self,
                 conversation_state: ConversationState,
                 user_state: UserState,
                 dialog: Dialog,):
        if conversation_state is None:
            raise Exception(
                "[DoctorOnlineUABot]: Missing parameter. conversation_state is required"
            )
        if user_state is None:
            raise Exception("[DoctorOnlineUABot]: Missing parameter. user_state is required")
        if dialog is None:
            raise Exception("[DoctorOnlineUABot]: Missing parameter. dialog is required")
        self.conversation_state = conversation_state
        self.conversation_data_accessor = self.conversation_state.create_property("ConversationData")
        self.user_state = user_state
        self.dialog = dialog

    async def on_turn(self, turn_context: TurnContext):
        await super().on_turn(turn_context)
        await self.conversation_state.save_changes(turn_context, False)
        await self.user_state.save_changes(turn_context, False)

    async def on_members_added_activity(self, members_added: List[ChannelAccount], turn_context: TurnContext):
        if turn_context.activity.channel_id == 'msteams':
            for member in members_added:
                if member.id != turn_context.activity.recipient.id:
                    activity = await create_welcome_activity()
                    await turn_context.send_activity(activity)
        else:
            for member in members_added:
                if member.id != turn_context.activity.recipient.id:
                    hello_msg = "Продовжуючи користуватись ботом ви погоджуєтесь з " \
                                "[правилами користування](https://doctoronline.bsmu.edu.ua/terms) та " \
                                "[політикою конфіденційності](https://doctoronline.bsmu.edu.ua/privacy) сервісу."
                    await turn_context.send_activity(hello_msg)
                    zero_stage = ("Дитячі Лікарі", "Дорослі лікарі", "Псих. допомога")
                    await zero_stage_funct(zero_stage, turn_context)
                    return web.Response(status=200)

    async def on_message_activity(self, turn_context: TurnContext):
        if turn_context.activity.channel_id == 'msteams':
            conversation_data = await self.conversation_data_accessor.get(turn_context, ConversationData)
            await DialogHelper.run_dialog(
                self.dialog,
                turn_context,
                self.conversation_state.create_property("DialogState"), conversation_data
            )
        else:
            try:
                conversation_data = await self.conversation_data_accessor.get(turn_context, ConversationData)
                return await dialog_view(turn_context, conversation_data)
            except Exception:
                var = traceback.format_exc()
                print(var)
                response = "Трапилась помилка, спробуйте пізніше"
                await turn_context.send_activity(response)

    async def on_token_response_event(self, turn_context: TurnContext):
        # Run the Dialog with the new Token Response Event Activity.
        conversation_data = await self.conversation_data_accessor.get(turn_context, ConversationData)
        await DialogHelper.run_dialog(
            self.dialog,
            turn_context,
            self.conversation_state.create_property("DialogState"), conversation_data
        )

    async def on_sign_in_invoke(self, turn_context: TurnContext):
        # Invoked when a signIn invoke activity is received from the connector.
        conversation_data = await self.conversation_data_accessor.get(turn_context, ConversationData)
        await DialogHelper.run_dialog(
            self.dialog,
            turn_context,
            self.conversation_state.create_property("DialogState"), conversation_data,
        )

    async def on_teams_signin_verify_state(self, turn_context: TurnContext):
        conversation_data = await self.conversation_data_accessor.get(turn_context, ConversationData)
        await DialogHelper.run_dialog(
            self.dialog,
            turn_context,
            self.conversation_state.create_property("DialogState"), conversation_data,
        )

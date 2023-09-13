import streamlit as st
import os
import asyncio

from session_state import get
from httpx_oauth.clients.google import GoogleOAuth2

async def write_authorization_url(client,
                                  redirect_uri):
    authorization_url = await client.get_authorization_url(
        redirect_uri,
        scope=["profile", "email"],
        extras_params={"access_type": "offline"},
    )
    return authorization_url

async def write_access_token(client,
                             redirect_uri,
                             code):
    token = await client.get_access_token(code, redirect_uri)
    return token

async def get_email(client,
                    token):
    user_id, user_email = await client.get_id_email(token)
    return user_id, user_email

def main(user_id, user_email):
    st.write(f"Teste!!!")
    st.write(f"You're logged in as {user_email}")


if __name__ == '__main__':
    #client_id = "80547735486-qlqurma8i51tkdr8aqp5lncb25in1snd.apps.googleusercontent.com"
    #client_id = "80547735486-t57afr5fb28g5o3075fh2rib6n93p08q.apps.googleusercontent.com"
    client_id = "80547735486-v27sr7scvtldgdagtj5gpf8ke2bquoph.apps.googleusercontent.com"
    #client_secret = "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"
    #client_secret = "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"
    client_secret = "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"
    redirect_uri = "https://autorregulacao.streamlit.app"
    #redirect_uri = "http://localhost:8501/"
    #client_id = os.environ['GOOGLE_CLIENT_ID']
    #client_secret = os.environ['GOOGLE_CLIENT_SECRET']
    #redirect_uri = os.environ['REDIRECT_URI']

    client = GoogleOAuth2(client_id, client_secret)
    authorization_url = asyncio.run(
        write_authorization_url(client=client,
                                redirect_uri=redirect_uri)
    )

    session_state = get(token=None)
    if session_state.token is None:
        try:
            code = st.experimental_get_query_params()['code']
        except:
            st.write(f'''<h1>
                Please login using this <a target="_self"
                href="{authorization_url}">url</a></h1>''',
                     unsafe_allow_html=True)
        else:
            # Verify token is correct:
            try:
                token = asyncio.run(
                    write_access_token(client=client,
                                       redirect_uri=redirect_uri,
                                       code=code))
            except:
                st.write(f'''<h1>
                    This account is not allowed or page was refreshed.
                    Please try again: <a target="_self"
                    href="{authorization_url}">url</a></h1>''',
                         unsafe_allow_html=True)
            else:
                # Check if token has expired:
                if token.is_expired():
                    if token.is_expired():
                        st.write(f'''<h1>
                        Login session has ended,
                        please <a target="_self" href="{authorization_url}">
                        login</a> again.</h1>
                        ''')
                else:
                    session_state.token = token
                    user_id, user_email = asyncio.run(
                        get_email(client=client,
                                  token=token['access_token'])
                    )
                    session_state.user_id = user_id
                    session_state.user_email = user_email
                    main(user_id=session_state.user_id,
                         user_email=session_state.user_email)
    else:
        main(user_id=session_state.user_id,
             user_email=session_state.user_email)

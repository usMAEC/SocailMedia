import token, secrets, asyncio, requests

from postproxy import (PostProxy, PlatformParams,
    FacebookParams,
    InstagramParams,
    TikTokParams,
    YouTubeParams,
    PinterestParams,
    LinkedInParams,
    ThreadsParams,
    ThreadChildInput,
    TwitterParams,
    )
from firebase import *
from flask import  Flask, flash, redirect, url_for, session, request, render_template, jsonify, send_from_directory
from functools import wraps
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}) # Allow all, or specify
app.secret_key = 'supersecretkey'  # Replace with your own secret key
API_KEY = "3c259e69ea7cb71eb594cba145b50628c939be87648f191e"

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login', next=request))
        return f(*args,**kwargs)
    return decorated_function

async def createPPProfile(replacedEmail):
    async with PostProxy(API_KEY) as client:
        groups = (await client.profile_groups.list()).data
        for g in groups:
            if g.name == replacedEmail:
                raise ValueError("Such email group is already existx")
            
        group = await client.profile_groups.create(replacedEmail);
    return group

@app.route('/linkPlatform')
async def linkPPProfilePlatform():
    async with PostProxy(API_KEY) as client:
        platform = request.args.get('platform')
        ppProfileGroupId = session.get('ppProfileGroupId')

        conn = await client.profile_groups.initialize_connection(
            ppProfileGroupId,
            platform= platform, #"tiktok"
            redirect_url= request.host_url + "callback",
        )
        return redirect(conn.url)
    
async def main():
    async with PostProxy(API_KEY) as client:
        # List profile groups
        
        groups = (await client.profile_groups.list()).data
        print("Profile groups:")
        for g in groups:
            print(f"  {g.id}: {g.name} ({g.profiles_count} profiles)")

        # Use the first group (or create one)
        if groups:
            group = groups[0]
        else:
            group = await client.profile_groups.create("My Group")
            print(f"\nCreated group: {group.id}")

        # Initialize a connection for a platform
        conn = await client.profile_groups.initialize_connection(
            group.id,
            platform="tiktok",
            redirect_url= request.host_url + "callback",
        )
        #redirect(conn.url)
        #print(f"\nRedirect the user to: {conn.url}")

        return conn

@app.route('/myaccount')
def myaccount():
     return render_template('sidebarbase.html')

@app.route('/mychannel')
def mychannel():
     return render_template('mychannel.html')
    
@app.route('/callback')
@login_required
def authorize():
    return redirect('/')

@app.route('/')
async def index():
    if not session.get('user'):
        return render_template('index.html')
    return  redirect(url_for('profile'))

    #con = await main()
    #return redirect(con.url)


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


@app.route('/createLogin/', methods=('GET', 'POST'))
async def createLogin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if not email:
            flash('Email is required!')
        elif not password:
            flash('Password is required!')
        else:
            #messages.append({'title': title, 'content': content})
            try:
                replacedEmail = getPeriodReplacement(email)
                ppProfileGroup = await createPPProfile(replacedEmail)
                createUser(replacedEmail,password, ppProfileGroup.id)
                return redirect(url_for('index'))
            except :
                return render_template('createLogin.html')            
    return render_template('createLogin.html')

@app.route('/login/', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        
        if not email:
            flash('Email is required!')
        elif not password:
            flash('Password is required!')
        else:
            isValid, ppProfileGroupId = isValidUser(email, password)
            if isValid:
                session['user']= email
                session['ppProfileGroupId']= ppProfileGroupId
                return redirect(url_for('profile'))
            else:
                 flash('User or password is not valid!')
    return render_template('Login.html', formName='Login')

@app.route('/logout/', methods=('GET', 'POST'))
def logout():
    session.clear()
    return redirect(url_for('index'))

def getFilePath(userid):
    return f"./uploads/{getPeriodReplacement(userid)}"

@app.route('/schedule', methods=(['GET','POST']))
#@login_required
async def schedule():
    if request.method == 'POST':

        data = json.loads(json.dumps(request.form.to_dict()));
        #file = request.files['file']
        #filename = os.path.join('/Users/maec-inflow/Desktop/MyFlask/uploads', file.filename)
        #if file.filename == '':
        #    return 'No selected file'
        #if file:
        #    # Securely save the file    
        #    file.save(filename)

        
        #insertSchedule(session['user'], datetime.datetime.strptime(data.get('from_date'),dateformat), data);
        
        if(data.get('postnow')):
            print('continue uploading')
            ppProfileGroupId = session['ppProfileGroupId']
            async with PostProxy(API_KEY, profile_group_id=ppProfileGroupId) as client:

                profiles = (await client.profiles.list()).data; # profile from post proxy     
               
                filename = f"{getFilePath(session['user'])}/{data['fileName']}"
                pfs = PlatformParams()
                

                if data.get('youtube') == 'on':
                    pfs.youtube=YouTubeParams(
                        format="post",
                        title="My Video Title",
                        privacy_status="public",
                    )
                if data.get('twitter') == 'on':
                    pfs.twitter=TwitterParams(
                        format="post",
                        first_comment="First!",
                    )
                if data.get('facebook') == 'on':

                    facebook_profile = next(
                        (p for p in profiles if p.platform == "facebook"), None )
                    if facebook_profile is None:
                        raise ValueError("No Facebook profile found")

                    placements = (await client.profiles.placements(id=facebook_profile.id)).data

                    pfs.facebook=FacebookParams(
                        format="post",
                        page_id=placements[0].id,
                        first_comment="First!"
                    )
                if data.get('tiktok') == 'on':
                    pfs.tiktok=TikTokParams(
                        format="video",
                        privacy_status="PUBLIC_TO_EVERYONE",
                        auto_add_music=True,
                    )    
                if data.get('instagram') == 'on':
                    pfs.instagram=InstagramParams(
                        format="post",
                        #collaborators=["@collab_account"]
                    )
                if data.get('linkedin') == 'on':
                                pfs.linkedin=LinkedInParams(
                                    format="post",
                                    #collaborators=["@collab_account"]
                                )
                await post_with_local_file(ppProfileGroupId,filename, pfs)

            #if data.get('facebook') == 'on':
            #formatted_tickers, top_stocks_names, top_gainer, top_loser = format_tickers(["dgdg", "dssddd"])

            #thumbnail_path = generate_thumbnail(top_gainer, top_loser)
            ##if data.get('youtube'):
       
            #dt = datetime.strptime(data.get('from_date'));

        #insertSchedule(session['user'], datetime.datetime.strptime(data.get('from_date'),dateformat), data);
        return redirect(url_for('profile'))
    return render_template('Schedule.html')
    #response_data = {"status": "success", "received": data}
    #return jsonify(response_data)


async def post_with_local_file(PROFILE_GROUP_ID, filename, platforms):



    async with PostProxy(API_KEY, profile_group_id=PROFILE_GROUP_ID) as client:
        profiles = ( await client.profiles.list()).data

        platform_profiles = []
        allPlatforms = list(platforms.model_fields_set) 
        for aPf in allPlatforms:
            for pf in profiles: 
                if aPf == pf.platform:
                    platform_profiles.append(pf.id)


        post =  await client.posts.create(
            "Posted with a local file!",
            profiles=platform_profiles,
            draft=False,
            media_files=[filename],
            platforms=platforms
        )
        #await client.posts.publish_draft(post.id)
        print(f"Created post {post.id} with file upload — status: {post.status}")


async def draft_then_publish(PROFILE_GROUP_ID):
    """Create a draft post, then publish it."""
    async with PostProxy(API_KEY, profile_group_id=PROFILE_GROUP_ID) as client:


        # Create as draft
        post = await client.posts.create(
            "This starts as a draft",
            profiles=[PROFILE_GROUP_ID],
            draft=True,
        )
        print(f"Created draft {post.id} — status: {post.status}")

        # Publish the draft
        post = await client.posts.publish_draft(post.id)
        print(f"Published {post.id} — status: {post.status}")

@app.route('/getSchedule', methods=['GET'])
def get_items():
    return jsonify( getSchedue(session['user'], date.today().replace(day=1)+ timedelta(days=-6), last_day_of_month(date.today()) + timedelta(days=6)))



@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check for file in request
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file:
            fpath = getFilePath(session['user'])
            if not os.path.exists(fpath):
                os.mkdir(fpath)
            # Securely save the file
            filename = file.filename
            file.content_type
            fullfileName = os.path.join(fpath, filename) 
            file.save(fullfileName)
            return ({'filename': filename, 'filetype' : file.content_type})
    return ''


if __name__ == "__main__":
   app.run(debug=True)


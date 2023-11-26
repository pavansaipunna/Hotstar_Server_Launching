import cv2
import boto3
import time
from cvzone.HandTrackingModule import HandDetector


ec2 = boto3.resource('ec2')
elb = boto3.client('elbv2')
# list of all OS running
allOS = []


def LaunchOS():
    instances = ec2.create_instances(
        ImageId="ami-0a2acf24c0d86e927",
        MinCount=1,
        MaxCount=1,
        InstanceType="t2.micro",
        SecurityGroupIds=[
        'sg-0072cb1b72ca4eeaf',
    ],
    )

    OSid = instances[0].id
    allOS.append(OSid)
    
    time.sleep(30)
    elb.register_targets(TargetGroupArn='arn:aws:elasticloadbalancing:ap-south-1:881559863141:targetgroup/testtg/5eb53fb428255398',
    Targets=[
        {
            'Id': OSid,
        },
       
    ],
                    )
    
    # print(allOS)
    print("Total OS : " , len(allOS)


def TerminateOS():
    if allOS:
        myos = allOS.pop()
        response = ec2.instances.filter(InstanceIds=[myos]).terminate()
        
        elb.deregister_targets(TargetGroupArn='arn:aws:elasticloadbalancing:ap-south-1:881559863141:targetgroup/testtg/5eb53fb428255398',
    Targets=[
        {
            'Id': myos,
        },
       
    ],
                    )
        
        print("Remaining OS : " , len(allOS))
        return response
    else:
        print("no more OS is Running")


detector = HandDetector(maxHands=1,
                     detectionCon=0.8)


cap  = cv2.VideoCapture(0)


while True:
    ret, img = cap.read()
    cv2.imshow("Img" , img)
    if cv2.waitKey(1000) == 13:
        break

    hand = detector.findHands(img , draw=False)
    if hand:
        lmlist = hand[0]
        if lmlist:
            fingerup = detector.fingersUp(lmlist)
            print(fingerup)
            if fingerup == [0, 1, 0, 0, 0]:
                print("sec finger ..")
                TerminateOS()
            
            elif fingerup == [0, 1, 1, 0, 0]:
                print("2 and 3 finger ..")
                LaunchOS()

            
cv2.destroyAllWindows()


cap.release()  


#! /usr/bin/env python


"""
.. module:: motion_controller
	:platform: Unix
	:synopsis: Python module for the robot's motion controller

.. moduleauthor:: Shozab Abid hasanshozab10@gmail.com

This node controls the robot motion in the simulation. It waits for the user_interface node's request to start the simulation. When the request is recieved, it start the robot's exploration in which robot  visits all the three rooms in the environment. All rooms coordinates are predefined: R1(2,0) R2(0,2) R3(-2,0). Robot start the exploration from initial position P(1,1). After reaching in every room,  it request the 'hint_generator' node to provide the hint. Once hint is recieved, it request the 'oracle' node to load the that hint in the ARMOR reasoner and then move to visit next room. After visiting and reciving all the hints it start the reasoner to deduced the hypotheses and to check if the hypotheses based on previous loaded hints is consistent or not. If the hints are consistent then the robotgo to the origin position O(0,0) and print the hypotheses statement. Incase if the hypothesis is not consistent then the node will repeat the exploration. 
  
  
Service:
	/request_hint
	/oracle_service
	/user_interface

"""

import rospy
import time
from exporobot_assignment1.srv import Command, CommandResponse
from exporobot_assignment1.srv import Hint, HintResponse 
from exporobot_assignment1.srv import Oracle
from std_msgs.msg import String
from geometry_msgs.msg import Point

req_hint_client_ = None
"""rospy.ServiceProxy(): Initializing global variable with 'None' for initializing '/request_hint' service client.

"""

req_oracle_client_ = None
"""rospy.ServiceProxy(): Initializing global variable with 'None' for initializing '/oracle_service' service client.

"""

hypo_ = 0
"""Int: Initializing global variable with '0' for tracking the number of hypotheses.

"""  

  
def clbk_user_interface(msg):
	
	"""
	
	This function waits for the 'user_interface' node's request to start 
	the simulation. When the request with correct msg structure is recieved,
	it start the robot's exploration by calling the 'exploration()' function. 
	
	Args: 
		msg(Command): the input request message.
		
	Returns: 
		String 
	
	"""
	
	if (msg.req == "start"):
		 time.sleep(5) 
		 return exploration()
	else:
		print("req msg is not right.", msg.req)
		return CommandResponse("not done")

		
def exploration():

	"""
	
	This function starts the robot's exploration in which robot visits all the
	three rooms in the environment. It initializes all the rooms, origin and 
	robot starting position coordinates as R1(2,0) R2(0,2) R3(-2,0), O (0,0) and
	P (1,1). After reaching in every room,  it request the 'hint_generator' node
	to provide the hint. Once hint is recieved, it request the 'oracle' node to 
	load the that hint in the ARMOR reasoner and then move to visit next room. 
	After visiting and reciving all the hints it start the reasoner to deduced 
	the hypotheses and to check if the hypotheses based on previous loaded hints is
	consistent or not. If the hints are consistent then the robotgo to the origin
	position O(0,0) and print the hypotheses statement. Incase if the hypothesis is
	not consistent then the node will repeat the exploration.

	Args: 
		none
		
	Returns: 
		String 
	
	"""

	global hypo_
	who = "none"
	what = "none"
	where = "none"
	
	hypo_ += 1
	
	robot_curr_pos = Point()
	robot_curr_pos.x = 1
	robot_curr_pos.y = 1
	
	room1 = Point()
	room1.x = 2
	room1.y = 0

	room2 = Point()
	room2.x = 0
	room2.y = 2

	room3 = Point()
	room3.x = -2
	room3.y = 0
	
	origin = Point()
	origin.x = 0
	origin.y = 0	
	
	while 1:

		if(visit(robot_curr_pos, room1)):
			robot_curr_pos.x,robot_curr_pos.y = room1.x,room1.y
			rospy.loginfo('Robot is in Room1 (%i,%i). Now collecting hint.',robot_curr_pos.x,robot_curr_pos.y)
			time.sleep(2)
			
			# Now call hint service
			hint1 = req_hint_client_("need_hint",("HP"+str(hypo_)))
			
			if(hint1.res[0] == "who"):
				who = hint1.res[2]
			elif(hint1.res[0] == "what"):
				what = hint1.res[2]
			elif(hint1.res[0] == "where"):
				where = hint1.res[2]
			
			rospy.loginfo('Collected hint from room1 ["%s", "%s", "%s"]',hint1.res[0],hint1.res[1],hint1.res[2])
			
			# Now call hint load service
			rospy.loginfo('Loading the hint in reasoner.')
			oracle_load_hint1 = req_oracle_client_(hint1.res[0], hint1.res)		
		else:
			rospy.loginfo('Robot was not able to reach room1.')
			return("not done")
			break
	
		if(robot_curr_pos.x,robot_curr_pos.y == room1.x,room1.y and oracle_load_hint1.res == True):
			rospy.loginfo('Hint successfully loaded in the reasoner.')
			time.sleep(1)		
			if(visit(robot_curr_pos, room2)):
				robot_curr_pos.x,robot_curr_pos.y = room2.x,room2.y
				rospy.loginfo('Robot is in Room2 (%i,%i). Now collecting hint.',robot_curr_pos.x,robot_curr_pos.y)
				time.sleep(2)
		
				# Now call hint service
				hint2 = req_hint_client_("need_hint",("HP"+str(hypo_)))
		
				if(hint2.res[0] == "who"):
					who = hint2.res[2]
				elif(hint2.res[0] == "what"):
					what = hint2.res[2]
				elif(hint2.res[0] == "where"):
					where = hint2.res[2]	
			
				rospy.loginfo('Collected hint from room2  ["%s", "%s", "%s"]',hint2.res[0],hint2.res[1],hint2.res[2])
		
				# Now call hint load service
				rospy.loginfo('Loading the hint in reasoner.')
				oracle_load_hint2 = req_oracle_client_(hint2.res[0], hint2.res)
			else:
				rospy.loginfo('Robot was not able to reach room2.')
				return("not done")
				break

		if(robot_curr_pos.x,robot_curr_pos.y == room2.x,room2.y and oracle_load_hint2.res == True):
			rospy.loginfo('Hint successfully loaded in the reasoner.')
			time.sleep(1)
			if(visit(robot_curr_pos, room3)):
				robot_curr_pos.x,robot_curr_pos.y = room3.x,room3.y
				rospy.loginfo('Robot is in Room3 (%i,%i). Now collecting hint.',robot_curr_pos.x,robot_curr_pos.y)
				time.sleep(2)
				
				# Now call hint service
				hint3 = req_hint_client_("need_hint",("HP"+str(hypo_)))
				
				if(hint3.res[0] == "who"):
					who = hint3.res[2]
				elif(hint3.res[0] == "what"):
					what = hint3.res[2]
				elif(hint3.res[0] == "where"):
					where = hint3.res[2]
		
		
				rospy.loginfo('Collected hint from room3  ["%s", "%s", "%s"]',hint3.res[0],hint3.res[1],hint3.res[2])
				
				# Now call hint load service
				rospy.loginfo('Loading the hint in reasoner.')
				oracle_load_hint3 = req_oracle_client_(hint3.res[0], hint3.res)
			
			else:
				rospy.loginfo('Robot was not able to reach room3.')
				return("not done")
				break			

		if(robot_curr_pos.x,robot_curr_pos.y == room3.x,room3.y and oracle_load_hint3.res == True):
			
			rospy.loginfo('Hint successfully loaded in the reasoner.')
			
			time.sleep(1)
				
			rospy.loginfo('Collected hints from all three rooms. Now starting the reasoner.')
			
			# Starting reasoner
			oracle_start_reason = req_oracle_client_('REASON', []) 
			
			# Checking if inconsistency > prev_inconsistency:
			if(oracle_start_reason.res == True):
				
				rospy.loginfo('Reasoner started successfully. Now, checking the consistency of the hypothesis..')
				
				oracle_check_consis = req_oracle_client_('CONSISTENT', []) 
				
				time.sleep(1)
			
				if (oracle_check_consis.res == True):
					
					rospy.loginfo('Hypothesis found conistence. Now going to origin.')
					
					if(visit(robot_curr_pos, origin)):
					
						robot_curr_pos.x,robot_curr_pos.y = origin.x, origin.y
					
						rospy.loginfo('Robot reached origin (%i,%i).',robot_curr_pos.x,robot_curr_pos.y)
						
						rospy.loginfo('HYPOTHESIS STATEMENT: %s with the %s in the %s',who,what,where)
					
						return("done")
					
					else:
						
						rospy.loginfo('Robot was not able to reach origin.')
						
						return("not done")
						
						break
				else:
					
					rospy.loginfo('Hypothesis found inconistence. Repeating the exploration.')
		
		hypo_ += 1
		
		
def visit(current,goal):

	"""
	
	This function controls the robot's movement during the simulation, making
	it move from one point to another in the environemnt. It takes to arguement
	current position of the robot and goal position of the robot. It calculate 
	the distance between to points and move robot in a way to reduce this distance. 
	
	Args: 
		current(Point()): Current position of the robot. 
		goal(Point()): Target position of the robot. 		
		
	Returns: 
		Bool 
	
	"""

	curr_pos = Point()
	curr_pos.x, curr_pos.y =  current.x,current.y
	dist = ((((goal.x - curr_pos.x)**2)+((goal.y - curr_pos.y)**2))**0.5)
	dist = round(dist,2)
	vel_factor = 0.1
	while not dist <= 0.05:
		
		if (goal.x-curr_pos.x)>0:	vel_x = vel_factor*1 
		else:  vel_x = vel_factor*-1
		
		if (goal.y-curr_pos.y)>0:	vel_y = vel_factor*1 
		else:  vel_y = vel_factor*-1
		
		curr_pos.x += round(vel_x,2)
		curr_pos.y += round(vel_y,2)
		dist = ((((goal.x - curr_pos.x)**2)+((goal.y - curr_pos.y)**2))**0.5)
		dist = round(dist,2)	
		rospy.loginfo('Robot moving (%f,%f), dist(%f)',curr_pos.x,curr_pos.y,dist)	
		time.sleep(1)
		
	if(dist <= 0.05):
		return True
	else:
		return False

	
def main():

	"""
	
	This is a 'main' function of  'motion_controller' node. It initializes
	clients for '/request_hint' service hosted by 'hint_generator' node, and
	'/oracle_service' service which is hosted by 'oracle' node and lastly a 
	server for '/user_interface' service. Upon recieving request for 
	'/user_interface' service it calls the '/clbk_user_interface' function.  
	
	Args: 
		none		
		
	Returns: 
		none
	
	"""

	global req_hint_client_
	global req_oracle_client_
	rospy.init_node('motion_controller')
	req_hint_client_ = rospy.ServiceProxy('/request_hint', Hint)
	req_oracle_client_ = rospy.ServiceProxy('/oracle_service', Oracle)
	user_server = rospy.Service('/user_interface', Command, clbk_user_interface)
	rospy.spin()

if __name__ == '__main__':
    main()

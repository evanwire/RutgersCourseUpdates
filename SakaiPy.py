# -*- coding: utf-8 -*-
import SakaiSession
import json
from datetime import date
import re


class SakaiPy(object):
    """
    The main entry point for the program. Use this class to access all of the other tools.
    """

    def __init__(self):
        """
        Create the main SakaiPy object. This object will be the main interface point.
        """
        
        #Open config.json to extract relevant user info
        with open("config.json", "r") as read_file:
            self.data = json.load(read_file)["data"]
        
        self.sitesList = self.data["sites-list"]
        
        #Create the session
        connectioninfo = self.data["info"]
        self.session = SakaiSession.SakaiSession(connectioninfo['username'], connectioninfo['password'],
                                                 connectioninfo['baseurl'])
        
        self.sessionInfo = self.session.get_session_info()


    def get_announcements(self, verbose=False):
        """
        Get a list of all assignments in the sites listed in the config.json file
        
        Params:
            -verbose: if true, returns all announcements for all sites in the list for all time
                      if false, only returns announcements that were announced after the user's prior sakai login
        """
        announcement_list = []
        
        for site in self.sitesList:
            announcement = self.session.executeRequest('GET', '/announcement/site/{}.json'.format(site))
            if announcement["announcement_collection"]:
                for a in announcement["announcement_collection"]:
                    if verbose:
                        announcement_list.append(self.clean_announcement(a))
                    else:
                        if a["createdOn"] > self.sessionInfo["lastAccessedTime"]:
                            announcement_list.append(self.clean_announcement(a))
        
        if not announcement_list:
            return "No announcements :)"
        return announcement_list


    def get_assignments(self): #TODO: make a clean_assignments method once one of my classes releases any assignments
        """
        Get a list of all assignments in the sites listed in the config.json file
        """
        
        assignment_list = []
        
        for site in self.sitesList:
            assignment = self.session.executeRequest('GET', '/assignment/site/{}.json'.format(site))
            if assignment["assignment_collection"]:
                assignment_list.extend(assignment["assignment_collection"])
        
        
        if not assignment_list:
            return "No assignments :)"
        return assignment_list

    def cleanhtml(self, raw_html):
        """
        Cleans all html tags from a string
        """
        cleanr = re.compile('<.*?>|\\xa0')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext
    
    def clean_announcement(self, a):
        """
        Cleans an announcement so only relevant fields are stored
        """
        siteTitle = a["siteTitle"]
        title = a["title"]
        body = self.cleanhtml(a["body"])
        return {"siteTitle": siteTitle, "title": title, "body": body}
        
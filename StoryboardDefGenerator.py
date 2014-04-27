import os,sys,shutil,optparse,re,io


rootDir = ""

# ------------------------------------| Options Parser |----------------------------------------------

# Parse options
parser = optparse.OptionParser()
parser.add_option('-r', '--root', 	help='specify root dir to search from', dest="rootDir")
parser.add_option('-d', '--dest', 	help='specify dest path to output generated files', default="./generated",dest="dest_res")

(opts, args) = parser.parse_args()

if not opts.rootDir:
	rootDir = os.path.abspath('../');
else:
	rootDir = opts.rootDir;

opts.dest_res = os.path.abspath(opts.dest_res);
print "root dir: " + os.path.abspath(rootDir);
print "dest dir: " + opts.dest_res;

# ------------------------------------| Methods |----------------------------------------------

# Find all storyboards in path
def storyboardsInPath(path):
	all_files = []
	for root, dirs, files in os.walk(path, topdown=False):
		for name in files:
			all_files.append(os.path.join(root, name));
	result = []
	for fitem in all_files:
		if "/.git/" not in fitem and os.path.splitext(fitem)[1] == ".storyboard":
			result.append(fitem)
		
	return result

# debug print each storyboard filename and each controllers storyboardIdentifier
def printStoryboardDictionary():
	for key in storyboardDict:
		files = storyboardDict[key];
		# print "StoryBoard: " + key
		print "-----" + key +  " Storyboard----"
		for name in files:
			print "" + name



# Parse each storyboard in pathlist and extract dictionary with filename and controller names
# dict[filename] = [storyboardIdentifier]
def parseStoryBoards(path_list):
	dictionary = {}
	for path in path_list:
		storyfile = io.open(path,"r").read()
		filename = os.path.basename(path).split('.')[0]
		dictionary[filename] = []


		matches = re.findall(r'(storyboardIdentifier=")(.*?)"',storyfile)
		if matches:
			for group in matches:
				name = group[1]
				# print "name: " + name
				dictionary[filename].append(name)
	return dictionary;



# ------------------------------------| Script Body |----------------------------------------------



# Find all storyboard paths from root
storyboardPaths = storyboardsInPath(rootDir)

# Parse each storyboard and extract filename and storyboardIdentifiers
storyboardDict = parseStoryBoards(storyboardPaths);

# Debug print
# printStoryboardDictionary()


# Create Destination Path

folderPath = opts.dest_res
if not os.path.exists(folderPath):
    os.makedirs(folderPath)

storyPathHeader = os.path.join(opts.dest_res,'StoryBoardManager.h');
storyPathMain = os.path.join(opts.dest_res,'StoryBoardManager.m');
if not (os.path.exists( storyPathHeader ) or os.path.exists(storyPathMain)) :
	head = io.open(storyPathHeader,'w',encoding='utf8'); 
	head.write( u""" 
//
//  StoryBoardManager.h
//
//  Created by Simon Coulter
//

#import <Foundation/Foundation.h>
#import "_StoryBoardManager.h"

@interface StoryBoardManager : _StoryBoardManager

@end 

		""");
	head.close();

	mainT = io.open(storyPathMain,'w',encoding='utf8');
	mainT.write(u""" 
//
//  StoryBoardManager.m
//
//  Created by Simon Coulter
//

@implementation StoryBoardManager

@end	""");
	mainT.close();
# --------------------------------------------------------------------------------------------------
# ------------------------------- Template Header Here ---------------------------------------------
# --------------------------------------------------------------------------------------------------

# TODO: cleanup and generalize this code (its crap i know)

headerPath = os.path.join(opts.dest_res,'_StoryBoardManager.h');
header = io.open(headerPath,'w',encoding='utf8')

header.write( u"""
// Created by Simon Coulter 


// ******* Careful this file is auto-generated *********

#import <Foundation/Foundation.h>

@interface _StoryBoardManager : NSObject

""");

for filename in storyboardDict:
	header.write("+ (UIStoryboard*)" + unicode(filename.lower()) + "StoryBoard;\n")


header.write(u"""+ (UIViewController*)viewController:(NSString*)viewControlelrID inStoryBoard:(NSString*)storyboardID;

@end 

// StoryBoardIDs

""")
for filename in storyboardDict:
	header.write("static NSString* StoryBoardID_" + unicode(filename.capitalize()) + "= @\"" + unicode(filename) + "\";\n")


header.write(u"\n\n// Controller ID's \n")

for filename in storyboardDict:
	for controllerName in storyboardDict[filename]:
		header.write("static NSString* SB" + filename.capitalize() + "_" + controllerName.capitalize() + " = @\"" + controllerName + "\";\n")

header.write(u'\n\n')

header.close()

# --------------------------------------------------------------------------------------------------
# ------------------------------- Template Main Here ---------------------------------------------
# --------------------------------------------------------------------------------------------------


mainPath = os.path.join(opts.dest_res,'_StoryBoardManager.m');
main = io.open(mainPath,'w',encoding='utf8')

main.write( u""" 
//
//  _StoryBoardManager.m
//
//  Created by Simon Coulter 
//


// ******* Careful this file is auto-generated *********


#import "_StoryBoardManager.h"

@implementation _StoryBoardManager

""");

for filename in storyboardDict:
	main.write(u"+ (UIStoryboard*)" + filename.lower() + "StoryBoard\n{\n");
	main.write(u"    return [UIStoryboard storyboardWithName:StoryBoardID_" + filename.capitalize() + " bundle:nil];\n}\n");

main.write(u"""


+ (UIViewController*)viewController:(NSString*)controllerName inStoryBoard:(NSString*)storyboardID
{
    UIStoryboard* storyboard = [UIStoryboard storyboardWithName:storyboardID bundle:nil];
    UIViewController* controller = (UIViewController*)[storyboard instantiateViewControllerWithIdentifier:controllerName];
    return controller;
}

@end
""");

main.close();

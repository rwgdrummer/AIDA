###
###	File:		FaceIndex/Makefile
###
###	Description:	For building the FaceIndex library for an OS.
###			There is also a test program.
###
###	When invoking make, the following shell variables may be set:
###
###	PROJ			Provides the root directory of the project.
###	THIRD_PARTY_CPPFLAGS 	Provides -I flags for the location(s) of OpenBR, Qt5,
###				and OpenCV (et. al.) header files.
###	THIRD_PARTY_LDFLAGS	Provides -L flags for the location(s) of OpenBR, Qt5,
###				and OpenCV (et. al.) shared libraries.
###	DEST			Specifies the directory path into which the FaceIndex
###				library and include files will be copied by the install
###				target.  Defaults to $(PROJ)/built.
###


PROJ ?=			.
WS =			$(PROJ)/..

DEST ?=			$(PROJ)/built

THIRD_PARTY_CPPFLAGS ?=	-I$(WS)/ThirdParty/Includes
THIRD_PARTY_LDFLAGS ?=	-L$(WS)/ThirdParty/SharedLibs

CPPFLAGS +=		-march=x86-64 -std=$(LANG) -Wall \
			-I. $(THIRD_PARTY_CPPFLAGS)

LDFLAGS +=		-march=x86-64 \
			-L. $(THIRD_PARTY_LDFLAGS)

DEST_BIN_DIR =		$(DEST)/bin
DEST_INCL_DIR =		$(DEST)/include
DEST_LIB_DIR =		$(DEST)/lib


comma:=			,
empty:=			
space:=			$(empty) $(empty)

EXE_RPATHS =		-Wl,-rpath,$(EXE_RPATH) \
			-Wl,-rpath,$(EXE_RPATH)/../lib
LIB_RPATHS =		-Wl,-rpath,$(LIB_RPATH) \
			-Wl,-rpath,$(LIB_RPATH)/../lib

RPATH_LINK_PATHS =	$(patsubst -L%,%,$(subst $(space)-L,:,$(THIRD_PARTY_LDFLAGS)))
EXE_RPATHS +=		-Wl$(subst :,$(comma)-rpath$(comma),$(subst :./,:$(EXE_RPATH)/,:$(RPATH_LINK_PATHS)))
LIB_RPATHS +=		-Wl$(subst :,$(comma)-rpath$(comma),$(subst :./,:$(LIB_RPATH)/,:$(RPATH_LINK_PATHS)))

EXE_LDFLAGS =		$(EXE_RPATHS)
ifeq ($(firstword $(shell ld -v 2>&1)),GNU)
EXE_LDFLAGS +=		-Wl,-rpath-link,$(RPATH_LINK_PATHS)
endif

CC =			$(CXX)
LANG =			c++14


OS =			$(shell uname)

ifeq (${OS},Darwin)			## Mac OS X

LIB_PREFIX =		lib
SHARED_LIB_EXT =	.dylib

CPPFLAGS +=		-iframework /opt/local/libexec/qt5/lib \
			-isystem /opt/local/libexec/qt5/lib/QtCore.framework/Headers

OS_SPECIFIC_LIBS =	-F/opt/local/libexec/qt5/lib -framework QtCore \
			-lc++

LIB_LDFLAGS =		-dynamiclib \
			-install_name @rpath/$(@F) \
			$(LIB_RPATHS)

EXE_RPATH =		@executable_path
LIB_RPATH =		@loader_path

else ifeq (${OS},Linux)			## Linux

LIB_PREFIX =		lib
SHARED_LIB_EXT =	.so

CPPFLAGS +=		-fPIC -D_DEFAULT_SOURCE

OS_SPECIFIC_LIBS =	-lpthread -lstdc++ -lm

LIB_LDFLAGS =		-shared -Wl,-Bsymbolic,-soname,$(@F) \
			$(LIB_RPATHS)

EXE_RPATH =		'$$ORIGIN'
LIB_RPATH =		'$$ORIGIN'

endif


#OPT_FLAGS +=		-O3
DEBUG_FLAGS +=		-g
CPPFLAGS +=		$(OPT_FLAGS) $(DEBUG_FLAGS)


FACE_LIB_INCLS =	FaceIndex.hh
FACE_LIB_OBJS =		FaceIndex.o
FACE_LIB =		$(LIB_PREFIX)FaceIndex$(SHARED_LIB_EXT)

INDEX_FACES =		IndexFaces
INDEX_FACES_OBJS =	TestFaceIndex.o

TEST_RECOG =		TestFaceRecognition
TEST_RECOG_OBJS =	$(TEST_RECOG).o

LIBS =			-lopenbr

OPENCV_LIBS =		-lopencv_photo \
			-lopencv_xfeatures2d \
			-lopencv_shape \
			-lopencv_video \
			-lopencv_ml \
			-lopencv_calib3d \
			-lopencv_features2d \
			-lopencv_highgui \
			-lopencv_videoio \
			-lopencv_flann \
			-lopencv_imgcodecs \
			-lopencv_objdetect \
			-lopencv_imgproc \
			-lopencv_core \
			-ljpeg -lpng -ltiff -lz


###
###	Targets
###


.PHONY:			all \
			clean \
			install \
			uninstall

all:			$(INDEX_FACES)

clean:
	- $(RM) $(FACE_LIB_OBJS) $(FACE_LIB)
	- $(RM) $(INDEX_FACES) $(INDEX_FACES_OBJS)
	- $(RM) $(TEST_RECOG) $(TEST_RECOG_OBJS)
	- $(RM) *.o *.c~ *.h~ *.vect

install:		$(FACE_LIB) $(INDEX_FACES) \
			| $(DEST_BIN_DIR) $(DEST_INCL_DIR) $(DEST_LIB_DIR)
	cp $(FACE_LIB) $(DEST_LIB_DIR)/
	cp $(FACE_LIB_INCLS) $(DEST_INCL_DIR)/
	cp $(INDEX_FACES) $(DEST_BIN_DIR)/

uninstall:
	- $(RM) $(DEST_BIN_DIR)/$(INDEX_FACES)
	- $(RM) $(DEST_LIB_DIR)/$(FACE_LIB)
	- $(RM) $(FACE_LIB_INCLS:%=$(DEST_INCL_DIR)/%)

$(DEST_BIN_DIR) \
$(DEST_INCL_DIR) \
$(DEST_LIB_DIR):
	- mkdir -p $@

$(FACE_LIB):		$(FACE_LIB_OBJS)
	$(CXX) -o $@ $^ \
		$(LDFLAGS) $(LIB_LDFLAGS) \
		$(LIBS) $(OPENCV_LIBS) \
		$(OS_SPECIFIC_LIBS)

$(INDEX_FACES):		$(INDEX_FACES_OBJS) \
			| $(FACE_LIB)
	$(CXX) -o $@ $^ \
		$(LDFLAGS) $(EXE_LDFLAGS) \
		-lFaceIndex \
		$(LIBS) $(OPENCV_LIBS) \
		$(OS_SPECIFIC_LIBS)

$(TEST_RECOG):		$(TEST_RECOG_OBJS)
	$(CXX) -o $@ $^ \
		$(CPPFLAGS) \
		$(LDFLAGS) $(EXE_LDFLAGS) \
		$(LIBS) $(OPENCV_LIBS) \
		$(OS_SPECIFIC_LIBS)

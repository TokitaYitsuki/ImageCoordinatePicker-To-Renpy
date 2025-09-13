# ImageCoordinatePicker-To-Renpy
This is a program made with Python that helps Ren'Py developers arrange the UI and confirm the UI's position relative to the background coordinates.

#以下是本程序的使用说明：

#The following is the user manual for this program:

(The English translation is provided by Bing Translate.)

打开exe文件后你可以看到这个界面。After opening the exe file, you can see this interface.
<img width="1738" height="1031" alt="2" src="https://github.com/user-attachments/assets/cf2d7303-1ec1-4988-85be-fd28dd8077b0" />
如上图所示，我们通过红色框内的按钮控制两种不同的模式，分别为默认的“坐标获取模式”与切换后的“叠加图片模式”。
As shown in the figure above, we control two different modes through the button in the red box, namely the default "Coordinate Acquisition Mode" and the switched "Overlay Image Mode".

坐标获取模式：
Coordinate acquisition mode:


在默认“坐标获取”的状态下，可以使用"加载背景图片"按钮添加背景图片，此时程序会自动缩放放置图片，当鼠标指针移动到图片任意位置时，底部按钮上会自动显示指针所在的坐标与RGB信息。
In the default state of 'Coordinate Acquisition', you can use the 'Load Background Image'(加载背景图片) button to add a background image. The program will automatically scale the image, and when the mouse pointer moves to any position on the image, the coordinates and RGB information of the pointer's location will be automatically displayed on the bottom button.

并且，我们可以点击加载的图片，生成以此图片为基准的坐标点的标注点。在“坐标点列表”选中坐标可以使用“修改坐标”以自主更改该点的桌标，亦可以使用“添加坐标”以自主添加单个坐标，选中并点击“删除坐标”可以删除单个坐标。
Furthermore, we can click on the loaded image to generate annotation points based on the coordinates of that image. In the 'Coordinate Point List'(坐标点列表), selecting a coordinate allows us to use 'Modify Coordinate' (修改坐标)to independently change the label of that point, or we can use 'Add Coordinate' (添加坐标)to independently add a single coordinate. Selecting and clicking 'Delete Coordinate' (删除坐标)allows us to delete a single coordinate.

如果你有批量的坐标点，我们可以使用底部的“导入坐标”来导入批量的坐标，它支持以空格、中文“，”、英文“,”分隔的xy坐标例如:(10 10)(10，10)(10,10)，点击底部的“清除坐标点”可以直接清除所有坐标，当然切换为叠加图片模式时也会清理所有自主添加的所有坐标。
If you have a batch of coordinate points, we can use the "Import Coordinates" (导入坐标)at the bottom to import a batch of coordinates, which supports xy coordinates separated by spaces, "，", or "," such as: (10 10)(10，10)(10,10). Clicking the "Clear Coordinates" (清除坐标点)at the bottom will directly clear all coordinates. Of course, when switching to the overlay image mode, it will also clear all self-added coordinates.


叠加图片模式：
Overlay image mode:

切换到叠加功能后，程序会自动清除所有坐标点，使用底部的“添加叠加图片”或“批量添加图片”可以添加单张/多张图片，添加后在“叠加图片列表”会自动更新带有此图片名称和坐标的选项，并且在坐标列表会显示此图片的坐标。
After switching to the overlay function, the program will automatically clear all coordinate points. You can use the "Add Overlay Image" (添加叠加图片)or "Batch Add Images" (批量添加图片)at the bottom to add single or multiple images. After adding, the "Overlay Image List" (叠加图片列表)will automatically update with the options that include the name and coordinates of the image, and the coordinates of this image will be displayed in the coordinate list.

导入了图片后，导入的图片默认状态是解锁状态，我们可以拖动它到画板的任意位置，这个图片会自动获取背景图片的缩放倍率以自适应大小，它向您展示的位置将会与在Ren'py中放置时一致。您也可以使用叠加列表下的功能按钮“设置坐标”来自主调节图像的位置，也可以列表中选中并使用“重命名”以自主更改单个图片的名称。
After importing the image, the default state of the imported image is unlocked, allowing us to drag it to any position on the canvas. This image will automatically adopt the scaling factor of the background image to adjust its size, and the position it shows you will be consistent with where it was placed in Ren'py. You can also use the 'Set Coordinates' (设置坐标)function button under the overlay list to manually adjust the image's position, and select it in the list to use 'Rename' (重命名)to change the name of a single image.

在叠加列表功能键中，我设置了"锁定叠加图片"功能，选中单个图片并点击会锁定图片防止误触不需要移动的图片。选中并点击"删除图片"会删除选中的图片。
In the overlay list function key, I have set the "Lock Overlay Image" (锁定叠加图片)feature, which locks the image when a single image is selected and clicked to prevent accidentally moving the image that does not need to be moved. Selecting and clicking "Delete Image" (删除图片)will delete the selected image.

叠加图片列表中“置顶”是强行消除所有叠加图片并重新显示的按钮，它能解决本程序极容易出现的背景图片覆盖叠加的图片的问题，尽管它很蠢，但它是一个仍是编程初学者的作者能想出的最有效的解决方法。
The 'Top' (置顶)button in the overlay image list forcefully removes all overlay images and redisplays them. It can solve the issue where the background image easily covers the overlay images in this program. Although it is very stupid, but it is the most effective solution that a beginner programmer could come up with.

底部功能键“保存数据”可以导出设置的全部坐标信息，txt文件格式如下：
The bottom function key 'Save Data' (保存数据)can export all the configured coordinate information, and the txt file format is as follows:

                背景图片尺寸:1920x1080

                坐标点(包含叠加图片位置):
                (-100,100)
                (200,400)
                (768,239)

                叠加图片位置(左上角基准点):
                n1(-100,100)
                n2(200,400)


这个程序是作者的第一次制作，它有很多BUG，例如添加叠加图片后不会更新背景图片的相应坐标点，需要切换坐标获取模式才加载，然后叠加图片就被覆盖。这些错误主要集中在图层加载顺序问题上，作者已经尽力通过各种方式减小影响。希望我的程序能帮助到您，感谢使用我的项目。
This program is the author's first production, and it has many bugs. For example, after adding an overlay image, the corresponding coordinates of the background image do not update; you need to switch the coordinate acquisition mode to load it, and then the overlay image gets covered. These errors mainly focus on issues with the loading order of layers, and the author has tried various methods to minimize the impact. I hope my program can help you, and thank you for using my project.


#The English translation comes from machine translation; please forgive any errors in expression.

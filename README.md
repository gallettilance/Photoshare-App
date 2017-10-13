# CS660_Project1
Hi I compared the official sql with ours, and add the following changes accordingly:
1. add ON DELETE CASCADE to the "album"--because when a user is deleted, the albums created by him/her should disappear too
2. add ON DELETE CASCADE to the "friend_with" relation, since when any part of the friendship is deleted, then this relationship should be deleted too.
3. add ON DELETE CASCADE to the "likes" relationship, since if either the user or the photo is deleted, then this relationship does not exist. 
4. The note on the official sql file says we cannot name the above relationship as "like", but should name it as "LIKETABLE"--do you know why? 


For best template rendering please execute in Google Chrome


Hi I added the pdf version of our diagram above:)
Hi to view the diagram, please go to https://www.draw.io/#Hgalletti94%2FCS660_Project1%2Fmaster%2Fdatabase%2FCS660_ERmodel_Project1.xml

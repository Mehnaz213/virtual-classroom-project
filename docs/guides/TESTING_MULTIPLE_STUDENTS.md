# Testing Multiple Students in Focus Mate

## ✅ System Already Supports Multiple Students!

The backend is designed to handle unlimited students joining the same session.

## 🧪 How to Test with 2 Students:

### Step 1: Teacher Creates Session
1. Open: http://localhost:5178
2. Login as teacher: `demo.teacher@focusmate.com` / `teacher123`
3. Create a new session (e.g., "Math Class")
4. Note the session code (e.g., "ABC123")

### Step 2: Student 1 Joins
1. Open: http://localhost:5178 in **Browser 1** (or incognito window)
2. Login as: `demo.student1@focusmate.com` / `student123`
3. Enter session code from teacher
4. Allow webcam access
5. System starts monitoring Student 1

### Step 3: Student 2 Joins
1. Open: http://localhost:5178 in **Browser 2** (different browser or another incognito window)
2. Login as: `demo.student2@focusmate.com` / `student123`
3. Enter the SAME session code
4. Allow webcam access
5. System starts monitoring Student 2

### Step 4: Teacher Views Both Students
1. Go back to teacher dashboard
2. You should see:
   - **Attendance table** showing both students
   - **Real-time updates** from both students
   - **Individual engagement levels** for each
   - **Timeline** showing both students' activities

## 📊 What Teacher Sees:

### Attendance Table:
| Name | Lock Mode | Last Seen | Status |
|------|-----------|-----------|--------|
| Demo Student 1 | Off | 5:30:15 PM | ENGAGED |
| Demo Student 2 | Off | 5:30:18 PM | PARTIAL |

### Dashboard Updates:
- Engagement meter shows average of all students
- Timeline shows events from all students
- Alerts show issues from any student
- Label breakdown aggregates all students

## 🔑 Available Test Accounts:

### Teacher:
- Email: `demo.teacher@focusmate.com`
- Password: `teacher123`

### Students:
1. Email: `demo.student1@focusmate.com` / Password: `student123`
2. Email: `demo.student2@focusmate.com` / Password: `student123`
3. Email: `demo.student3@focusmate.com` / Password: `student123`
4. Email: `demo.student4@focusmate.com` / Password: `student123`
5. Email: `demo.student5@focusmate.com` / Password: `student123`

## 💡 Tips:

1. **Use Different Browsers**: Chrome + Firefox, or multiple incognito windows
2. **Check Console**: Open F12 in each student window to see detection logs
3. **Refresh Dashboard**: Teacher dashboard updates every 5 seconds
4. **Test Movements**: Have each student look in different directions
5. **Watch Real-time**: See how teacher dashboard shows both students' data

## 🎯 Expected Behavior:

✅ Multiple students can join with same code
✅ Each student monitored independently
✅ Teacher sees all students in attendance table
✅ Dashboard aggregates data from all students
✅ Real-time updates for each student
✅ Individual engagement levels tracked
✅ Timeline shows all students' events

## 🐛 Troubleshooting:

**Student not showing up?**
- Refresh teacher dashboard
- Check if student successfully joined (should see "Joined..." message)
- Verify webcam is working (check video feed)

**Data not updating?**
- Check browser console for errors
- Verify backend is running (http://localhost:8000)
- Check network tab for API calls

**Can't login as second student?**
- Use a different browser or incognito window
- Clear cookies if needed
- Make sure you're using different student accounts

## 🚀 Ready to Test!

The system is fully ready for multiple students. Just follow the steps above!

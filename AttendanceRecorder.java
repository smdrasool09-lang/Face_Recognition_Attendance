// src/attendance/AttendanceRecorder.java
package attendance;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.Timestamp;
import java.util.Date;

public class AttendanceRecorder {
    public static void main(String[] args) {
        if (args.length < 1) {
            System.out.println("⚠ No student name provided!");
            return;
        }

        String studentName = args[0];
        String section = args.length > 1 ? args[1] : "Unknown";
        String department = args.length > 2 ? args[2] : "Unknown";

        if ("Unknown".equalsIgnoreCase(studentName)) {
            System.out.println("👀 Face detected but not recognized. Attendance not recorded.");
            return;
        }

        String url = "jdbc:mysql://localhost:3306/AttendanceDB?useSSL=false&serverTimezone=UTC";
        String user = "root";
        String password = "your_password"; // TODO: set your actual password

        String sql = "INSERT INTO attendance (name, section, department, timestamp) VALUES (?, ?, ?, ?)";

        try {
            Class.forName("com.mysql.cj.jdbc.Driver");

            try (Connection conn = DriverManager.getConnection(url, user, password);
                 PreparedStatement stmt = conn.prepareStatement(sql)) {

                stmt.setString(1, studentName);
                stmt.setString(2, section);
                stmt.setString(3, department);
                stmt.setTimestamp(4, new Timestamp(new Date().getTime()));

                int rows = stmt.executeUpdate();
                if (rows > 0) {
                    System.out.println("\n✔ Attendance marked for student");
                    System.out.println("Name       : " + studentName);
                    System.out.println("Section    : " + section);
                    System.out.println("Department : " + department);
                } else {
                    System.out.println("⚠ No record inserted!");
                }
            }
        } catch (Exception e) {
            System.out.println("⚠ Error recording attendance: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
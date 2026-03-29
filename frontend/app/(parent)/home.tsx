import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import axios from 'axios';
import { getAuthHeader } from '../../src/store/authStore';
import { useBrandingStore } from '../../src/store/brandingStore';

const API_URL = 'https://absence-alert-4.preview.emergentagent.com';

interface Student {
  _id: string;
  name: string;
  roll_number: string;
  class_name: string;
  attendance_percentage: number;
  total_days: number;
  present_days: number;
}

export default function ParentHomeScreen() {
  const { branding } = useBrandingStore();
  const [students, setStudents] = useState<Student[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null);

  useEffect(() => {
    loadChildren();
  }, []);

  const loadChildren = async () => {
    try {
      const headers = await getAuthHeader();
      const response = await axios.get(`${API_URL}/api/parent/children`, { headers });
      setStudents(response.data);
      if (response.data.length > 0) {
        setSelectedStudent(response.data[0]);
      }
    } catch (error) {
      console.error('Failed to load children:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadChildren();
    setRefreshing(false);
  };

  const getAttendanceColor = (percentage: number) => {
    if (percentage >= 90) return '#10b981';
    if (percentage >= 75) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      <View style={[styles.header, { backgroundColor: branding.primary_color }]}>
        <Text style={styles.welcomeText}>Welcome to {branding.app_name}</Text>
        <Text style={styles.schoolName}>{branding.school_name}</Text>
      </View>

      {students.length === 0 ? (
        <View style={styles.emptyState}>
          <Ionicons name="people-outline" size={64} color="#cbd5e1" />
          <Text style={styles.emptyText}>No children linked</Text>
          <Text style={styles.emptySubtext}>Contact your teacher for registration</Text>
        </View>
      ) : (
        <>
          {students.length > 1 && (
            <View style={styles.studentSelector}>
              {students.map((student) => (
                <TouchableOpacity
                  key={student._id}
                  style={[
                    styles.studentTab,
                    selectedStudent?._id === student._id && {
                      backgroundColor: branding.primary_color,
                    },
                  ]}
                  onPress={() => setSelectedStudent(student)}
                >
                  <Text
                    style={[
                      styles.studentTabText,
                      selectedStudent?._id === student._id && styles.studentTabTextActive,
                    ]}
                  >
                    {student.name}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          )}

          {selectedStudent && (
            <View style={styles.content}>
              <View style={styles.studentCard}>
                <View style={styles.studentHeader}>
                  <View style={[styles.avatar, { backgroundColor: branding.primary_color + '20' }]}>
                    <Ionicons name="person" size={48} color={branding.primary_color} />
                  </View>
                  <View style={styles.studentInfo}>
                    <Text style={styles.studentName}>{selectedStudent.name}</Text>
                    <Text style={styles.studentDetails}>
                      Roll: {selectedStudent.roll_number} • Class: {selectedStudent.class_name}
                    </Text>
                  </View>
                </View>
              </View>

              <View style={styles.statsCard}>
                <Text style={styles.sectionTitle}>Attendance Overview</Text>

                <View style={styles.attendanceCircle}>
                  <View
                    style={[
                      styles.percentageCircle,
                      {
                        borderColor: getAttendanceColor(selectedStudent.attendance_percentage),
                      },
                    ]}
                  >
                    <Text
                      style={[
                        styles.percentageText,
                        { color: getAttendanceColor(selectedStudent.attendance_percentage) },
                      ]}
                    >
                      {selectedStudent.attendance_percentage}%
                    </Text>
                    <Text style={styles.percentageLabel}>Attendance</Text>
                  </View>
                </View>

                <View style={styles.statsRow}>
                  <View style={styles.statItem}>
                    <Text style={styles.statValue}>{selectedStudent.total_days}</Text>
                    <Text style={styles.statLabel}>Total Days</Text>
                  </View>
                  <View style={styles.statItem}>
                    <Text style={[styles.statValue, { color: '#10b981' }]}>
                      {selectedStudent.present_days}
                    </Text>
                    <Text style={styles.statLabel}>Present</Text>
                  </View>
                  <View style={styles.statItem}>
                    <Text style={[styles.statValue, { color: '#ef4444' }]}>
                      {selectedStudent.total_days - selectedStudent.present_days}
                    </Text>
                    <Text style={styles.statLabel}>Absent</Text>
                  </View>
                </View>
              </View>

              <View style={styles.quickActions}>
                <Text style={styles.sectionTitle}>Quick Actions</Text>

                <TouchableOpacity style={styles.actionCard}>
                  <Ionicons name="calendar-outline" size={24} color={branding.primary_color} />
                  <Text style={styles.actionText}>View Attendance History</Text>
                  <Ionicons name="chevron-forward" size={20} color="#94a3b8" />
                </TouchableOpacity>

                <TouchableOpacity style={styles.actionCard}>
                  <Ionicons name="book-outline" size={24} color={branding.primary_color} />
                  <Text style={styles.actionText}>View Homework</Text>
                  <Ionicons name="chevron-forward" size={20} color="#94a3b8" />
                </TouchableOpacity>
              </View>
            </View>
          )}
        </>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  header: {
    padding: 24,
    paddingTop: 32,
  },
  welcomeText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  schoolName: {
    fontSize: 14,
    color: '#fff',
    marginTop: 4,
    opacity: 0.9,
  },
  studentSelector: {
    flexDirection: 'row',
    padding: 16,
    gap: 8,
  },
  studentTab: {
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 20,
    backgroundColor: '#e2e8f0',
  },
  studentTabText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#64748b',
  },
  studentTabTextActive: {
    color: '#fff',
  },
  content: {
    padding: 16,
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 64,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#64748b',
    marginTop: 16,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#94a3b8',
    marginTop: 8,
  },
  studentCard: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  studentHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 16,
  },
  studentInfo: {
    flex: 1,
  },
  studentName: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1e293b',
  },
  studentDetails: {
    fontSize: 14,
    color: '#64748b',
    marginTop: 4,
  },
  statsCard: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1e293b',
    marginBottom: 16,
  },
  attendanceCircle: {
    alignItems: 'center',
    marginVertical: 24,
  },
  percentageCircle: {
    width: 160,
    height: 160,
    borderRadius: 80,
    borderWidth: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  percentageText: {
    fontSize: 40,
    fontWeight: 'bold',
  },
  percentageLabel: {
    fontSize: 14,
    color: '#64748b',
    marginTop: 4,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#f1f5f9',
  },
  statItem: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1e293b',
  },
  statLabel: {
    fontSize: 12,
    color: '#64748b',
    marginTop: 4,
  },
  quickActions: {
    marginTop: 8,
  },
  actionCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  actionText: {
    flex: 1,
    fontSize: 16,
    fontWeight: '500',
    color: '#1e293b',
    marginLeft: 12,
  },
});

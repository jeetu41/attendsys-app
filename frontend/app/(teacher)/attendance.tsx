import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  RefreshControl,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import axios from 'axios';
import Constants from 'expo-constants';
import { getAuthHeader } from '../../src/store/authStore';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { format } from 'date-fns';

const API_URL = Constants.expoConfig?.extra?.EXPO_PUBLIC_BACKEND_URL || 'http://localhost:8001';

interface Student {
  _id: string;
  name: string;
  roll_number: string;
  class_name: string;
  attendance_percentage: number;
}

interface AttendanceStatus {
  [studentId: string]: 'present' | 'absent' | 'late' | 'excused';
}

export default function AttendanceScreen() {
  const [students, setStudents] = useState<Student[]>([]);
  const [attendance, setAttendance] = useState<AttendanceStatus>({});
  const [selectedDate, setSelectedDate] = useState(format(new Date(), 'yyyy-MM-dd'));
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [offlineMode, setOfflineMode] = useState(false);

  useEffect(() => {
    loadStudents();
    loadTodayAttendance();
  }, []);

  const loadStudents = async () => {
    try {
      const headers = await getAuthHeader();
      const response = await axios.get(`${API_URL}/api/teacher/students`, { headers });
      setStudents(response.data);
    } catch (error) {
      console.error('Failed to load students:', error);
      // Try loading from offline storage
      const offlineData = await AsyncStorage.getItem('offline_students');
      if (offlineData) {
        setStudents(JSON.parse(offlineData));
        setOfflineMode(true);
      }
    }
  };

  const loadTodayAttendance = async () => {
    try {
      const headers = await getAuthHeader();
      const response = await axios.get(`${API_URL}/api/teacher/attendance/${selectedDate}`, { headers });
      const attendanceMap: AttendanceStatus = {};
      response.data.forEach((record: any) => {
        attendanceMap[record.student_id] = record.status;
      });
      setAttendance(attendanceMap);
    } catch (error) {
      console.error('Failed to load attendance:', error);
      // Try loading from offline storage
      const offlineData = await AsyncStorage.getItem(`offline_attendance_${selectedDate}`);
      if (offlineData) {
        setAttendance(JSON.parse(offlineData));
      }
    }
  };

  const toggleAttendance = (studentId: string, status: 'present' | 'absent' | 'late' | 'excused') => {
    setAttendance(prev => ({
      ...prev,
      [studentId]: prev[studentId] === status ? 'present' : status,
    }));
  };

  const saveAttendance = async () => {
    if (Object.keys(attendance).length === 0) {
      Alert.alert('No Records', 'Please mark attendance for at least one student');
      return;
    }

    setLoading(true);
    const records = Object.entries(attendance).map(([student_id, status]) => ({
      student_id,
      date: selectedDate,
      status,
    }));

    // Save to offline storage first
    await AsyncStorage.setItem(`offline_attendance_${selectedDate}`, JSON.stringify(attendance));

    try {
      const headers = await getAuthHeader();
      await axios.post(`${API_URL}/api/teacher/attendance`, { records }, { headers });
      Alert.alert('Success', 'Attendance saved successfully');
      setOfflineMode(false);
    } catch (error: any) {
      console.error('Failed to save attendance:', error);
      Alert.alert(
        'Saved Offline',
        'Attendance saved locally. It will sync when you have internet connection.'
      );
      setOfflineMode(true);
    } finally {
      setLoading(false);
    }
  };

  const markAllPresent = () => {
    const allPresent: AttendanceStatus = {};
    students.forEach(student => {
      allPresent[student._id] = 'present';
    });
    setAttendance(allPresent);
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadStudents();
    await loadTodayAttendance();
    setRefreshing(false);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'present': return '#10b981';
      case 'absent': return '#ef4444';
      case 'late': return '#f59e0b';
      case 'excused': return '#6366f1';
      default: return '#64748b';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'present': return 'checkmark-circle';
      case 'absent': return 'close-circle';
      case 'late': return 'time';
      case 'excused': return 'information-circle';
      default: return 'help-circle';
    }
  };

  return (
    <View style={styles.container}>
      {offlineMode && (
        <View style={styles.offlineBanner}>
          <Ionicons name="cloud-offline" size={16} color="#fff" />
          <Text style={styles.offlineText}>Offline Mode - Data will sync when online</Text>
        </View>
      )}

      <View style={styles.header}>
        <View style={styles.dateContainer}>
          <Ionicons name="calendar" size={20} color="#6366f1" />
          <Text style={styles.dateText}>{format(new Date(selectedDate), 'MMMM dd, yyyy')}</Text>
        </View>
        <TouchableOpacity style={styles.quickButton} onPress={markAllPresent}>
          <Text style={styles.quickButtonText}>Mark All Present</Text>
        </TouchableOpacity>
      </View>

      <ScrollView
        style={styles.content}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        {students.length === 0 ? (
          <View style={styles.emptyState}>
            <Ionicons name="people-outline" size={64} color="#cbd5e1" />
            <Text style={styles.emptyText}>No students added yet</Text>
            <Text style={styles.emptySubtext}>Go to Students tab to add students</Text>
          </View>
        ) : (
          students.map((student) => (
            <View key={student._id} style={styles.studentCard}>
              <View style={styles.studentInfo}>
                <Text style={styles.studentName}>{student.name}</Text>
                <Text style={styles.studentDetails}>
                  Roll: {student.roll_number} • Class: {student.class_name}
                </Text>
              </View>

              <View style={styles.statusButtons}>
                {(['present', 'absent', 'late', 'excused'] as const).map((status) => (
                  <TouchableOpacity
                    key={status}
                    style={[
                      styles.statusButton,
                      attendance[student._id] === status && {
                        backgroundColor: getStatusColor(status),
                      },
                    ]}
                    onPress={() => toggleAttendance(student._id, status)}
                  >
                    <Ionicons
                      name={getStatusIcon(status) as any}
                      size={20}
                      color={attendance[student._id] === status ? '#fff' : getStatusColor(status)}
                    />
                  </TouchableOpacity>
                ))}
              </View>
            </View>
          ))
        )}
      </ScrollView>

      {students.length > 0 && (
        <View style={styles.footer}>
          <View style={styles.summary}>
            <Text style={styles.summaryText}>
              {Object.values(attendance).filter(s => s === 'present').length} Present •{' '}
              {Object.values(attendance).filter(s => s === 'absent').length} Absent
            </Text>
          </View>
          <TouchableOpacity
            style={[styles.saveButton, loading && styles.saveButtonDisabled]}
            onPress={saveAttendance}
            disabled={loading}
          >
            <Ionicons name="save" size={20} color="#fff" />
            <Text style={styles.saveButtonText}>
              {loading ? 'Saving...' : 'Save Attendance'}
            </Text>
          </TouchableOpacity>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  offlineBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f59e0b',
    padding: 8,
    gap: 8,
  },
  offlineText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e2e8f0',
  },
  dateContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  dateText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1e293b',
  },
  quickButton: {
    backgroundColor: '#eef2ff',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
  },
  quickButtonText: {
    color: '#6366f1',
    fontSize: 12,
    fontWeight: '600',
  },
  content: {
    flex: 1,
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
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  studentInfo: {
    marginBottom: 12,
  },
  studentName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1e293b',
  },
  studentDetails: {
    fontSize: 14,
    color: '#64748b',
    marginTop: 4,
  },
  statusButtons: {
    flexDirection: 'row',
    gap: 8,
  },
  statusButton: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f1f5f9',
  },
  footer: {
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#e2e8f0',
    padding: 16,
  },
  summary: {
    marginBottom: 12,
  },
  summaryText: {
    fontSize: 14,
    color: '#64748b',
    textAlign: 'center',
  },
  saveButton: {
    backgroundColor: '#6366f1',
    borderRadius: 12,
    paddingVertical: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
  },
  saveButtonDisabled: {
    opacity: 0.6,
  },
  saveButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});

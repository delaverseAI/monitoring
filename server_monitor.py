import os
import psutil
import requests
import subprocess
from datetime import datetime
from datetime import datetime, timedelta

def get_nginx_stats():
    """Fetch and calculate Nginx statistics including request rates"""
    try:
        response = requests.get('http://127.0.0.1/nginx_status', timeout=5)
        
        if response.status_code == 200:
            lines = response.text.strip().split('\n')
            stats = {}
            
            if lines[0].startswith('Active connections:'):
                stats['active_connections'] = int(lines[0].split(':')[1].strip())
            
            if len(lines) > 2:
                values = lines[2].split()
                if len(values) == 3:
                    stats['accepts'] = int(values[0])
                    stats['handled'] = int(values[1])
                    stats['requests'] = int(values[2])
            
            if len(lines) > 3 and lines[3].startswith('Reading:'):
                parts = lines[3].split()
                stats['reading'] = int(parts[1])
                stats['writing'] = int(parts[3])
                stats['waiting'] = int(parts[5])
            
            if 'requests' in stats and 'handled' in stats:
                stats['dropped_connections'] = stats['accepts'] - stats['handled'] if 'accepts' in stats else 0
                
                max_connections = 768
                stats['connection_usage_percent'] = round((stats['active_connections'] / max_connections) * 100, 2)
            
            try:
                now = datetime.now()
                one_minute_ago = now - timedelta(minutes=1)
                
                time_pattern = one_minute_ago.strftime('%d/%b/%Y:%H:%M')
                
                cmd = f"grep '{time_pattern}' /var/log/nginx/access.log | wc -l"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    requests_last_minute = int(result.stdout.strip())
                    stats['requests_per_minute'] = requests_last_minute
                    stats['requests_per_second'] = round(requests_last_minute / 60, 2)
                
                cmd_avg = f"grep '{time_pattern}' /var/log/nginx/access.log | awk '{{sum+=$NF; count++}} END {{if(count>0) print sum/count}}'"
                result_avg = subprocess.run(cmd_avg, shell=True, capture_output=True, text=True)
                
                if result_avg.returncode == 0 and result_avg.stdout.strip():
                    try:
                        stats['avg_response_time'] = round(float(result_avg.stdout.strip()), 3)
                    except:
                        pass
                        
                cmd_status = f"grep '{time_pattern}' /var/log/nginx/access.log | awk '{{print $9}}' | sort | uniq -c"
                result_status = subprocess.run(cmd_status, shell=True, capture_output=True, text=True)
                
                if result_status.returncode == 0:
                    status_codes = {}
                    for line in result_status.stdout.strip().split('\n'):
                        if line:
                            parts = line.strip().split()
                            if len(parts) == 2:
                                count, code = parts
                                status_codes[code] = int(count)
                    stats['status_codes'] = status_codes
                    
                    total_requests = sum(status_codes.values())
                    error_requests = sum(count for code, count in status_codes.items() if code.startswith('4') or code.startswith('5'))
                    if total_requests > 0:
                        stats['error_rate'] = round((error_requests / total_requests) * 100, 2)
                    
            except Exception as e:
                print(f"Error calculating request rates: {str(e)}")
            
            return stats
        
    except Exception as e:
        print(f"Error fetching nginx stats: {str(e)}")
    
    return None

def get_system_resources():
    """Get system resource usage (CPU, memory, disk)"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        
        cpu_count = psutil.cpu_count()
        
        memory = psutil.virtual_memory()
        
        disk = psutil.disk_usage('/')
        
        net_io = psutil.net_io_counters()
        
        boot_time = psutil.boot_time()
        current_time = datetime.now().timestamp()
        uptime_seconds = current_time - boot_time
        
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        
        uptime_str = f"{days}d {hours}h {minutes}m"
        
        process_count = len(psutil.pids())
        
        load_avg = os.getloadavg()
        
        return {
            'cpu': {
                'percent': cpu_percent,
                'count': cpu_count,
                'load_average': {
                    '1min': round(load_avg[0], 2),
                    '5min': round(load_avg[1], 2),
                    '15min': round(load_avg[2], 2)
                }
            },
            'memory': {
                'total': memory.total,
                'used': memory.used,
                'available': memory.available,
                'percent': memory.percent,
                'total_gb': round(memory.total / (1024**3), 2),
                'used_gb': round(memory.used / (1024**3), 2),
                'available_gb': round(memory.available / (1024**3), 2)
            },
            'disk': {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent,
                'total_gb': round(disk.total / (1024**3), 2),
                'used_gb': round(disk.used / (1024**3), 2),
                'free_gb': round(disk.free / (1024**3), 2)
            },
            'network': {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'bytes_sent_gb': round(net_io.bytes_sent / (1024**3), 2),
                'bytes_recv_gb': round(net_io.bytes_recv / (1024**3), 2)
            },
            'system': {
                'uptime': uptime_str,
                'boot_time': datetime.fromtimestamp(boot_time).strftime('%Y-%m-%d %H:%M:%S'),
                'process_count': process_count
            }
        }
        
    except Exception as e:
        print(f"Error getting system resources: {str(e)}")
        return None

def get_process_info():
    """Get information about key processes"""
    processes = []
    
    try:
        target_processes = ['nginx', 'python', 'node', 'php-fpm', 'mysql']
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                pinfo = proc.info
                for target in target_processes:
                    if target in pinfo['name'].lower():
                        processes.append({
                            'pid': pinfo['pid'],
                            'name': pinfo['name'],
                            'cpu_percent': round(pinfo['cpu_percent'], 2),
                            'memory_percent': round(pinfo['memory_percent'], 2),
                            'status': pinfo['status']
                        })
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        
        return processes[:10]
        
    except Exception as e:
        print(f"Error getting process info: {str(e)}")
        return []

def get_recommendations(resources, nginx_stats):
    """Generate recommendations based on resource usage"""
    recommendations = []
    
    if resources:
        if resources['cpu']['percent'] > 80:
            recommendations.append({
                'type': 'warning',
                'category': 'CPU',
                'message': 'CPU usage is high. Consider scaling up or optimizing processes.',
                'severity': 'high'
            })
        elif resources['cpu']['percent'] > 60:
            recommendations.append({
                'type': 'info',
                'category': 'CPU',
                'message': 'CPU usage is moderate. Monitor for increasing trends.',
                'severity': 'medium'
            })
        
        if resources['memory']['percent'] > 85:
            recommendations.append({
                'type': 'warning',
                'category': 'Memory',
                'message': 'Memory usage is critical. Consider adding more RAM or optimizing applications.',
                'severity': 'high'
            })
        elif resources['memory']['percent'] > 70:
            recommendations.append({
                'type': 'info',
                'category': 'Memory',
                'message': 'Memory usage is moderate. Keep monitoring for memory leaks.',
                'severity': 'medium'
            })
        
        if resources['disk']['percent'] > 90:
            recommendations.append({
                'type': 'error',
                'category': 'Disk',
                'message': 'Disk space is critically low! Clean up logs or increase storage immediately.',
                'severity': 'critical'
            })
        elif resources['disk']['percent'] > 80:
            recommendations.append({
                'type': 'warning',
                'category': 'Disk',
                'message': 'Disk space is running low. Plan for cleanup or expansion.',
                'severity': 'high'
            })
        
        cpu_count = resources['cpu']['count']
        if resources['cpu']['load_average']['1min'] > cpu_count * 2:
            recommendations.append({
                'type': 'warning',
                'category': 'Load',
                'message': f'System load is very high ({resources["cpu"]["load_average"]["1min"]} on {cpu_count} cores).',
                'severity': 'high'
            })
    
    if nginx_stats:
        if nginx_stats.get('waiting', 0) > 100:
            recommendations.append({
                'type': 'info',
                'category': 'Nginx',
                'message': 'High number of waiting connections. Consider tuning worker processes.',
                'severity': 'medium'
            })
    
    if not recommendations:
        recommendations.append({
            'type': 'success',
            'category': 'Overall',
            'message': 'All systems are running smoothly. No immediate action required.',
            'severity': 'low'
        })
    
    return recommendations
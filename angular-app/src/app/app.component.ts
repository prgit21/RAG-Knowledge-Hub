import { Component, OnInit } from '@angular/core';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { BrowserModule } from '@angular/platform-browser';
import { ApiService } from './api.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.sass'],
  providers:[HttpClientModule,BrowserModule,ApiService],
  
})
export class AppComponent implements OnInit {
  message: string = '';
  
  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.apiService.getHelloMessage().subscribe(
      (data) => {
        this.message = data.message;
        console.log(this.message)
      },
      (error) => {
        console.error('Error fetching message from backend:', error);
      }
    );
  }
}
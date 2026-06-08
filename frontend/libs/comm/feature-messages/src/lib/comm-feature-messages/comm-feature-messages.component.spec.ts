import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CommFeatureMessagesComponent } from './comm-feature-messages.component';

describe('CommFeatureMessagesComponent', () => {
  let component: CommFeatureMessagesComponent;
  let fixture: ComponentFixture<CommFeatureMessagesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CommFeatureMessagesComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(CommFeatureMessagesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
